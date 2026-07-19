from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted(ROOT.glob("*.ipynb"))
SDK_VERSION = "1.11.0"


def load_support():
    path = ROOT / "scripts" / "notebook_support.py"
    spec = importlib.util.spec_from_file_location("notebook_support", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUPPORT = load_support()


def notebook_source(notebook: Dict[str, Any]) -> str:
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


class FakeClient:
    calls: List[Dict[str, Any]] = []

    def __init__(self, **kwargs: Any):
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args: Any):
        return None

    def request(self, method: str, path: str, params=None, timeout=None):
        params = params or {}
        self.calls.append(
            {"method": method, "path": path, "params": params, "timeout": timeout}
        )
        symbol = params["by_code"]
        if path == "/v1/prices/latest":
            return {
                "data": {
                    "code": symbol,
                    "price": 80.0 if symbol == "WTI_USD" else 84.0,
                    "currency": "USD",
                    "unit": "barrel",
                    "source": "market_reporting",
                    "as_of": "2026-07-18T18:50:33Z",
                    "data_status": "current",
                }
            }
        if path == "/v1/prices/historical":
            start = datetime(2026, 4, 20, tzinfo=timezone.utc)
            offset = 0.0 if symbol == "WTI_USD" else 4.0
            records = []
            for day in range(90):
                at = start + timedelta(days=day)
                records.append(
                    {
                        "code": symbol,
                        "price": 75.0 + offset + day * 0.05 + ((day % 7) - 3) * 0.3,
                        "currency": "USD",
                        "unit": "barrel",
                        "source": "market_reporting",
                        "as_of": at.isoformat().replace("+00:00", "Z"),
                        "data_status": "current",
                    }
                )
            return {"data": {"prices": records}}
        raise AssertionError(f"Unexpected request path: {path}")


class NotebookContractTests(unittest.TestCase):
    def test_notebook_json_metadata_claims_and_outputs(self):
        self.assertEqual(len(NOTEBOOKS), 2)
        forbidden = [
            re.compile("1,000" + r"\s+requests/month\s+free", re.IGNORECASE),
            re.compile("100" + r"\s+requests\s+\(lifetime\)", re.IGNORECASE),
            re.compile("real" + r"[- ]?time\s+commodity\s+price", re.IGNORECASE),
            re.compile("98%" + r"\s+less\s+cost", re.IGNORECASE),
            re.compile("identify" + r"\s+trading\s+opportunities", re.IGNORECASE),
            re.compile("current" + r"\s+(price|spread):", re.IGNORECASE),
        ]
        required = [
            "https://api.oilpriceapi.com/product-facts.json",
            "OILPRICEAPI_KEY",
            "INVALID_KEY",
            "LOCKED_DATASET",
            "RATE_LIMITED",
            "TIMEOUT",
            "EMPTY_RESPONSE",
            "MALFORMED_RESPONSE",
            "/v1/prices/latest",
            "/v1/prices/historical",
            "source",
            "currency",
            "unit",
            "api_timestamp",
        ]

        for path in NOTEBOOKS:
            notebook = json.loads(path.read_text())
            source = notebook_source(notebook)
            self.assertEqual(notebook["nbformat"], 4)
            self.assertEqual(
                notebook["metadata"]["oilpriceapi"]["sdkVersion"], SDK_VERSION
            )
            self.assertTrue(notebook["metadata"]["oilpriceapi"]["outputsCleared"])
            self.assertIn(f"oilpriceapi[pandas]=={SDK_VERSION}", source)
            for phrase in required:
                self.assertIn(phrase, source, f"{path.name} missing {phrase}")
            for pattern in forbidden:
                self.assertIsNone(
                    pattern.search(source),
                    f"{path.name} contains {pattern.pattern}",
                )
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    self.assertIsNone(cell["execution_count"])
                    self.assertEqual(cell["outputs"], [])
                    cell_source = "".join(cell["source"])
                    if not cell_source.startswith("%pip"):
                        compile(cell_source, f"{path.name}:{cell['id']}", "exec")

    def test_embedded_support_code_matches_reviewed_source(self):
        expected = (ROOT / "scripts" / "notebook_support.py").read_text().strip()
        for path in NOTEBOOKS:
            notebook = json.loads(path.read_text())
            support_cells = [
                "".join(cell["source"]).strip()
                for cell in notebook["cells"]
                if cell["cell_type"] == "code" and cell["id"].endswith("support")
            ]
            self.assertEqual(support_cells, [expected])

    def test_exact_notebook_cells_execute_against_production_shaped_fixtures(self):
        import matplotlib

        matplotlib.use("Agg")
        with mock.patch.dict(
            os.environ, {"OILPRICEAPI_KEY": "fixture-key"}, clear=False
        ):
            for path in NOTEBOOKS:
                FakeClient.calls = []
                namespace: Dict[str, Any] = {"__name__": "__notebook_test__"}
                notebook = json.loads(path.read_text())
                for cell in notebook["cells"]:
                    if cell["cell_type"] != "code":
                        continue
                    source = "".join(cell["source"])
                    if source.startswith("%pip"):
                        continue
                    if cell["id"] in {"spread-fetch", "technical-fetch"}:
                        namespace["OilPriceAPI"] = FakeClient
                    exec(
                        compile(source, f"{path.name}:{cell['id']}", "exec"), namespace
                    )

                paths = [call["path"] for call in FakeClient.calls]
                self.assertIn("/v1/prices/latest", paths)
                self.assertIn("/v1/prices/historical", paths)
                self.assertTrue(all(call["timeout"] == 30 for call in FakeClient.calls))

    def test_recovery_and_payload_validation(self):
        self.assertEqual(SUPPORT.recovery_for_status(401)[0], "INVALID_KEY")
        self.assertEqual(SUPPORT.recovery_for_status(402)[0], "LOCKED_DATASET")
        self.assertEqual(SUPPORT.recovery_for_status(403)[0], "LOCKED_DATASET")
        self.assertEqual(SUPPORT.recovery_for_status(429)[0], "RATE_LIMITED")
        self.assertEqual(SUPPORT.recovery_for_exception(TimeoutError())[0], "TIMEOUT")
        self.assertEqual(
            SUPPORT.recovery_for_exception(json.JSONDecodeError("bad", "x", 0))[0],
            "MALFORMED_RESPONSE",
        )

        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "MISSING_SECRET"):
                SUPPORT.get_api_key()

        for payload in ({"data": None}, {"data": {"prices": []}}):
            with self.assertRaisesRegex(SUPPORT.NotebookDataError, "EMPTY_RESPONSE"):
                if payload["data"] is None:
                    SUPPORT.extract_latest(payload, "BRENT_CRUDE_USD")
                else:
                    SUPPORT.extract_history(payload, "BRENT_CRUDE_USD")

        malformed = {
            "data": {
                "code": "BRENT_CRUDE_USD",
                "price": "80.0",
                "currency": "USD",
                "unit": "barrel",
                "source": "market_reporting",
                "as_of": "2026-07-18T18:50:33Z",
            }
        }
        with self.assertRaisesRegex(SUPPORT.NotebookDataError, "MALFORMED_RESPONSE"):
            SUPPORT.extract_latest(malformed, "BRENT_CRUDE_USD")

        malformed["data"]["price"] = 80.0
        malformed["data"]["as_of"] = "2026-07-18T18:50:33"
        with self.assertRaisesRegex(SUPPORT.NotebookDataError, "has no timezone"):
            SUPPORT.extract_latest(malformed, "BRENT_CRUDE_USD")

        class StatusError(Exception):
            def __init__(self, status_code):
                super().__init__("credential-value-must-not-leak")
                self.status_code = status_code

        for status_code, expected_code in (
            (401, "INVALID_KEY"),
            (402, "LOCKED_DATASET"),
            (403, "LOCKED_DATASET"),
            (429, "RATE_LIMITED"),
            (503, "SERVER_ERROR"),
        ):
            with self.assertRaisesRegex(RuntimeError, f"^{expected_code}:") as raised:
                SUPPORT.safe_request(
                    lambda code=status_code: (_ for _ in ()).throw(StatusError(code))
                )
            self.assertNotIn("credential-value-must-not-leak", str(raised.exception))

    def test_kaggle_package_metadata_is_public_and_exact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            import scripts.package_kaggle as package_kaggle

            original_dist = package_kaggle.DIST
            package_kaggle.DIST = Path(temp_dir)
            try:
                package_kaggle.main()
                metadata_files = sorted(Path(temp_dir).glob("*/kernel-metadata.json"))
                self.assertEqual(len(metadata_files), 2)
                for metadata_file in metadata_files:
                    metadata = json.loads(metadata_file.read_text())
                    self.assertFalse(metadata["is_private"])
                    self.assertTrue(metadata["enable_internet"])
                    notebook_path = metadata_file.parent / metadata["code_file"]
                    self.assertTrue(notebook_path.exists())
                    self.assertNotIn("key", metadata["id"].lower())
            finally:
                package_kaggle.DIST = original_dist


if __name__ == "__main__":
    unittest.main()
