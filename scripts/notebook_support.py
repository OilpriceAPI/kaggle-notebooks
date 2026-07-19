"""Strict, secret-safe helpers embedded into the public Kaggle notebooks."""

from __future__ import annotations

import math
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


PRODUCT_FACTS_URL = "https://api.oilpriceapi.com/product-facts.json"
STATUS_URL = "https://status.oilpriceapi.com"


class NotebookDataError(RuntimeError):
    """Raised when a successful HTTP response is empty or unsafe to analyze."""


def get_api_key() -> str:
    """Read Kaggle Secrets first, then the local environment, without logging it."""
    api_key: Optional[str] = None
    try:
        from kaggle_secrets import UserSecretsClient  # type: ignore

        api_key = UserSecretsClient().get_secret("OILPRICEAPI_KEY")
    except ImportError:
        pass
    except Exception:
        # Kaggle raises when the named secret is absent or not attached.
        pass

    api_key = api_key or os.environ.get("OILPRICEAPI_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError(
            "MISSING_SECRET: add OILPRICEAPI_KEY through Kaggle Add-ons > Secrets "
            "or set it as a local environment variable. Never paste it into a cell."
        )
    return api_key.strip()


def recovery_for_status(status_code: Optional[int]) -> Tuple[str, str]:
    """Return a stable public error code and a working next action."""
    if status_code == 401:
        return (
            "INVALID_KEY",
            "Replace the key in Kaggle Secrets or the OilPriceAPI dashboard, then rerun.",
        )
    if status_code in (402, 403):
        return (
            "LOCKED_DATASET",
            "Review dataset access for the account at https://www.oilpriceapi.com/pricing.",
        )
    if status_code == 429:
        return (
            "RATE_LIMITED",
            "Wait for the API-provided reset window before rerunning this notebook.",
        )
    if status_code is not None and status_code >= 500:
        return (
            "SERVER_ERROR",
            f"Check {STATUS_URL}, then retry once or contact support with the request ID.",
        )
    return (
        "REQUEST_FAILED",
        f"Check {STATUS_URL} and the account, then contact support without sending the API key.",
    )


def recovery_for_exception(error: Exception) -> Tuple[str, str]:
    """Classify SDK/network failures without echoing response bodies or credentials."""
    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int):
        return recovery_for_status(status_code)

    error_name = type(error).__name__.lower()
    if "timeout" in error_name:
        return (
            "TIMEOUT",
            f"Reduce the date range, retry once, then check {STATUS_URL}.",
        )
    if "json" in error_name or "decode" in error_name:
        return (
            "MALFORMED_RESPONSE",
            "Retry once, then contact support with the request ID; do not send the API key.",
        )
    return recovery_for_status(None)


def safe_request(operation: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    """Run an SDK request and raise only a redacted, actionable notebook error."""
    try:
        payload = operation()
    except Exception as error:
        code, recovery = recovery_for_exception(error)
        raise RuntimeError(f"{code}: {recovery}") from None

    if not isinstance(payload, dict):
        raise NotebookDataError(
            "MALFORMED_RESPONSE: expected a JSON object. Retry once, then contact support."
        )
    return payload


def _required_text(record: Dict[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise NotebookDataError(
            f"MALFORMED_RESPONSE: record is missing required {field!r}; stop analysis and contact support."
        )
    return value.strip()


def _timestamp(record: Dict[str, Any]) -> Tuple[str, str]:
    for field in ("as_of", "source_timestamp", "timestamp", "created_at", "updated_at"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            try:
                parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
            except ValueError as error:
                raise NotebookDataError(
                    f"MALFORMED_RESPONSE: {field!r} is not an ISO timestamp; stop analysis."
                ) from error
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise NotebookDataError(
                    f"MALFORMED_RESPONSE: {field!r} has no timezone; stop analysis."
                )
            return value.strip(), field
    raise NotebookDataError(
        "MALFORMED_RESPONSE: record has no API timestamp; stop analysis and contact support."
    )


def normalize_record(record: Any, expected_symbol: str) -> Dict[str, Any]:
    """Preserve source semantics and reject defaults or invented values."""
    if not isinstance(record, dict):
        raise NotebookDataError("MALFORMED_RESPONSE: price record is not an object.")
    if isinstance(record.get("error"), str):
        raise NotebookDataError(
            "API_ERROR_PAYLOAD: the API returned an error object; review the commodity code and entitlement."
        )

    symbol = _required_text(record, "code")
    if symbol != expected_symbol:
        raise NotebookDataError(
            f"MALFORMED_RESPONSE: expected {expected_symbol}, received {symbol}; stop analysis."
        )

    price = record.get("price")
    if (
        isinstance(price, bool)
        or not isinstance(price, (int, float))
        or not math.isfinite(price)
    ):
        raise NotebookDataError(
            "MALFORMED_RESPONSE: price is not a finite number; stop analysis and contact support."
        )

    metadata = (
        record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    )
    source = record.get("source") or metadata.get("source")
    if not isinstance(source, str) or not source.strip():
        raise NotebookDataError(
            "MALFORMED_RESPONSE: source is missing; stop rather than attributing the value incorrectly."
        )

    api_timestamp, timestamp_field = _timestamp(record)
    freshness = record.get("data_status")
    if not isinstance(freshness, str):
        nested_freshness = record.get("freshness")
        if isinstance(nested_freshness, dict) and isinstance(
            nested_freshness.get("status"), str
        ):
            freshness = nested_freshness["status"]
        elif isinstance(record.get("stale"), bool):
            freshness = "stale" if record["stale"] else "current"
        else:
            freshness = "not_returned"

    return {
        "symbol": symbol,
        "price": float(price),
        "currency": _required_text(record, "currency"),
        "unit": _required_text(record, "unit"),
        "source": source.strip(),
        "api_timestamp": api_timestamp,
        "timestamp_field": timestamp_field,
        "freshness": freshness,
    }


def extract_latest(payload: Dict[str, Any], expected_symbol: str) -> Dict[str, Any]:
    data = payload.get("data")
    if data is None:
        raise NotebookDataError(
            "EMPTY_RESPONSE: no latest record was returned. Check the code and entitlement."
        )
    return normalize_record(data, expected_symbol)


def extract_history(
    payload: Dict[str, Any], expected_symbol: str
) -> List[Dict[str, Any]]:
    """Accept documented history envelopes while rejecting empty/malformed success."""
    data: Any = payload.get("data", payload)
    if isinstance(data, dict) and "data" in data and "prices" not in data:
        data = data["data"]
    if isinstance(data, dict) and "prices" in data:
        data = data["prices"]
    if isinstance(data, dict):
        records: Any = list(data.values())
    else:
        records = data

    if not isinstance(records, list):
        raise NotebookDataError(
            "MALFORMED_RESPONSE: history payload has no record list; stop analysis."
        )
    if not records:
        raise NotebookDataError(
            "EMPTY_RESPONSE: no history records were returned. Reduce or adjust the requested range."
        )
    return [normalize_record(record, expected_symbol) for record in records]
