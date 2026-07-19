#!/usr/bin/env python3
"""Generate deterministic, output-free Kaggle notebooks from reviewed source cells."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SDK_VERSION = "1.10.2"
CONTRACT_VERSION = "2026-07-18"
SUPPORT_SOURCE = (ROOT / "scripts" / "notebook_support.py").read_text()


def source_lines(source: str) -> List[str]:
    return source.strip().splitlines(keepends=True)


def markdown(cell_id: str, source: str) -> Dict[str, Any]:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source_lines(source),
    }


def code(cell_id: str, source: str) -> Dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source_lines(source),
    }


INSTALL_CELL = (
    f"""%pip install -q "oilpriceapi[pandas]=={SDK_VERSION}" matplotlib seaborn"""
)

IMPORT_CELL = """from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from oilpriceapi import OilPriceAPI

sns.set_theme(style="whitegrid")
EXECUTED_AT = datetime.now(timezone.utc)
END_DATE = EXECUTED_AT.date()
START_DATE = END_DATE - timedelta(days=90)
HISTORY_METHOD = "GET /v1/prices/historical with interval=daily"
print(f"Notebook execution (UTC): {EXECUTED_AT.isoformat()}")"""

RECOVERY_MARKDOWN = """## Recovery contract

The notebook fails closed and gives a next action for these states. It never prints
the API key, raw account response, or customer identifiers.

| State | Notebook code | Next action |
| --- | --- | --- |
| Missing Kaggle secret | `MISSING_SECRET` | Attach `OILPRICEAPI_KEY` through Kaggle Add-ons > Secrets. |
| HTTP 401 | `INVALID_KEY` | Replace the key in Secrets or the OilPriceAPI dashboard. |
| HTTP 402/403 | `LOCKED_DATASET` | Review account dataset access. |
| HTTP 429 | `RATE_LIMITED` | Wait for the API-provided reset window. |
| Timeout | `TIMEOUT` | Reduce the range, retry once, then check service status. |
| Empty success | `EMPTY_RESPONSE` | Adjust the range or code; do not chart an empty result. |
| Malformed success | `MALFORMED_RESPONSE` | Stop analysis and contact support with the request ID. |
"""

RECOVERY_ASSERTIONS = """assert recovery_for_status(401)[0] == "INVALID_KEY"
assert recovery_for_status(403)[0] == "LOCKED_DATASET"
assert recovery_for_status(429)[0] == "RATE_LIMITED"
assert recovery_for_exception(TimeoutError())[0] == "TIMEOUT"

for bad_payload in ({"data": []}, {"data": {"prices": []}}, {"data": {"prices": "bad"}}):
    try:
        extract_history(bad_payload, "BRENT_CRUDE_USD")
    except NotebookDataError as error:
        assert str(error).startswith(("EMPTY_RESPONSE", "MALFORMED_RESPONSE"))
    else:
        raise AssertionError("Invalid history payload was not rejected")

print("Recovery contract checks passed without making extra API requests.")"""

FETCH_HELPERS = """def fetch_symbol(client, symbol):
    latest_payload = safe_request(
        lambda: client.request(
            "GET",
            "/v1/prices/latest",
            params={"by_code": symbol},
            timeout=30,
        )
    )
    history_payload = safe_request(
        lambda: client.request(
            "GET",
            "/v1/prices/historical",
            params={
                "by_code": symbol,
                "start_date": START_DATE.isoformat(),
                "end_date": END_DATE.isoformat(),
                "interval": "daily",
                "per_page": 500,
            },
            timeout=30,
        )
    )
    return extract_latest(latest_payload, symbol), extract_history(history_payload, symbol)


def history_frame(records):
    frame = pd.DataFrame(records)
    frame["api_timestamp"] = pd.to_datetime(frame["api_timestamp"], utc=True)
    frame["api_date"] = frame["api_timestamp"].dt.floor("D")
    frame = frame.sort_values("api_timestamp").groupby("api_date", as_index=False).tail(1)
    return frame.set_index("api_date").sort_index()


def print_context(latest_rows, history_rows):
    context = pd.DataFrame(latest_rows)[
        [
            "symbol",
            "price",
            "currency",
            "unit",
            "source",
            "api_timestamp",
            "timestamp_field",
            "freshness",
        ]
    ]
    print("Latest-available record context; inspect timestamp and freshness before use:")
    print(context.to_string(index=False))
    print(f"Requested API record date range: {START_DATE} to {END_DATE}")
    print(f"History method: {HISTORY_METHOD}")
    print(f"History records returned: {sum(len(rows) for rows in history_rows)}")
    print("Limitation: cadence, history depth, and access vary by source, market hours, dataset, and account.")"""


SPREAD_INTRO = """# WTI and Brent Spread Analysis

This notebook compares API-timestamped WTI and Brent records returned by OilPriceAPI.
It is an educational analysis, not a trading signal or investment recommendation.

- SDK: `oilpriceapi[pandas]==1.10.2`
- Authentication: Kaggle Secrets label `OILPRICEAPI_KEY`
- [Reviewed product facts](https://api.oilpriceapi.com/product-facts.json) (contract 2026-07-18)
- [Current API documentation](https://docs.oilpriceapi.com/api-reference/prices/latest)
- [Data usage policy](https://www.oilpriceapi.com/legal/data-usage)

Latest available values include API timestamps. Cadence, history depth, and access
vary by source, market hours, dataset, and account entitlement. Stored outputs are
cleared in the repository copy; every public result must show its execution time."""

SPREAD_FETCH = """api_key = get_api_key()
with OilPriceAPI(api_key=api_key, timeout=30, max_retries=1, enable_telemetry=False) as client:
    wti_latest, wti_records = fetch_symbol(client, "WTI_USD")
    brent_latest, brent_records = fetch_symbol(client, "BRENT_CRUDE_USD")

print_context([wti_latest, brent_latest], [wti_records, brent_records])"""

SPREAD_ANALYSIS = """wti = history_frame(wti_records).rename(columns={"price": "WTI"})
brent = history_frame(brent_records).rename(columns={"price": "Brent"})

for label, frame in (("WTI", wti), ("Brent", brent)):
    if frame["currency"].nunique() != 1 or frame["unit"].nunique() != 1:
        raise NotebookDataError(f"MIXED_UNITS: {label} records cannot be compared safely.")

if wti["currency"].iloc[0] != brent["currency"].iloc[0] or wti["unit"].iloc[0] != brent["unit"].iloc[0]:
    raise NotebookDataError("INCOMPATIBLE_UNITS: WTI and Brent require explicit conversion before comparison.")

spread = wti[["WTI"]].join(brent[["Brent"]], how="inner")
if spread.empty:
    raise NotebookDataError("EMPTY_RESPONSE: no aligned API dates were returned.")
spread["Spread"] = spread["Brent"] - spread["WTI"]
spread["Spread_Pct"] = np.where(spread["WTI"] != 0, spread["Spread"] / spread["WTI"] * 100, np.nan)

print(f"Aligned API dates: {len(spread)}")
print(f"Last aligned API date: {spread.index.max().date()}")
print(spread.tail().to_string())"""

SPREAD_PLOT = """fig, (ax_price, ax_spread) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
ax_price.plot(spread.index, spread["WTI"], label="WTI", linewidth=2)
ax_price.plot(spread.index, spread["Brent"], label="Brent", linewidth=2)
ax_price.set_ylabel(f"Price ({wti['currency'].iloc[0]}/{wti['unit'].iloc[0]})")
ax_price.set_title("WTI and Brent by API timestamp")
ax_price.legend()

ax_spread.plot(spread.index, spread["Spread"], color="#237a57", linewidth=2)
ax_spread.axhline(0, color="#4b5563", linestyle="--", linewidth=1)
ax_spread.set_ylabel(f"Brent - WTI ({wti['currency'].iloc[0]}/{wti['unit'].iloc[0]})")
ax_spread.set_xlabel("API record date (UTC)")
ax_spread.set_title("Observed spread in the requested window")
plt.tight_layout()
plt.show()

summary = spread["Spread"].describe()[["count", "mean", "std", "min", "max"]]
print("Descriptive spread statistics for this execution:")
print(summary.to_string())"""

TECHNICAL_INTRO = """# API-Timestamped Brent Technical Indicators

This notebook calculates descriptive indicators from Brent records returned by
OilPriceAPI. Indicators summarize the requested sample; they do not forecast prices
or constitute a trading or investment recommendation.

- SDK: `oilpriceapi[pandas]==1.10.2`
- Authentication: Kaggle Secrets label `OILPRICEAPI_KEY`
- [Reviewed product facts](https://api.oilpriceapi.com/product-facts.json) (contract 2026-07-18)
- [Current API documentation](https://docs.oilpriceapi.com/api-reference/prices/latest)
- [Data usage policy](https://www.oilpriceapi.com/legal/data-usage)

Latest available values include API timestamps. Cadence, history depth, and access
vary by source, market hours, dataset, and account entitlement. Stored outputs are
cleared in the repository copy; every public result must show its execution time."""

TECHNICAL_FETCH = """api_key = get_api_key()
with OilPriceAPI(api_key=api_key, timeout=30, max_retries=1, enable_telemetry=False) as client:
    brent_latest, brent_records = fetch_symbol(client, "BRENT_CRUDE_USD")

print_context([brent_latest], [brent_records])"""

TECHNICAL_ANALYSIS = """history = history_frame(brent_records)
if history["currency"].nunique() != 1 or history["unit"].nunique() != 1:
    raise NotebookDataError("MIXED_UNITS: indicator input contains multiple currencies or units.")
if len(history) < 50:
    raise NotebookDataError("INSUFFICIENT_HISTORY: at least 50 API dates are required for this analysis.")

analysis = history[["price"]].rename(columns={"price": "Price"})
analysis["SMA_20"] = analysis["Price"].rolling(20).mean()
analysis["SMA_50"] = analysis["Price"].rolling(50).mean()
analysis["EMA_20"] = analysis["Price"].ewm(span=20, adjust=False).mean()
delta = analysis["Price"].diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()
relative_strength = gain / loss.replace(0, np.nan)
analysis["RSI_14"] = 100 - (100 / (1 + relative_strength))
analysis["Return_Pct"] = analysis["Price"].pct_change() * 100

print(f"API record dates analyzed: {len(analysis)}")
print(f"Last API date: {analysis.index.max().date()}")
print(analysis.tail().to_string())"""

TECHNICAL_PLOT = """fig, (ax_price, ax_rsi) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
ax_price.plot(analysis.index, analysis["Price"], label="Price", color="#111827", linewidth=2)
ax_price.plot(analysis.index, analysis["SMA_20"], label="20-date SMA", linewidth=1.5)
ax_price.plot(analysis.index, analysis["SMA_50"], label="50-date SMA", linewidth=1.5)
ax_price.set_ylabel(f"Price ({history['currency'].iloc[0]}/{history['unit'].iloc[0]})")
ax_price.set_title("Brent observations and moving averages by API timestamp")
ax_price.legend()

ax_rsi.plot(analysis.index, analysis["RSI_14"], color="#6d28d9", linewidth=1.5)
ax_rsi.axhline(70, color="#b91c1c", linestyle="--", linewidth=1)
ax_rsi.axhline(30, color="#237a57", linestyle="--", linewidth=1)
ax_rsi.set_ylabel("RSI (14 API dates)")
ax_rsi.set_xlabel("API record date (UTC)")
ax_rsi.set_ylim(0, 100)
plt.tight_layout()
plt.show()

last = analysis.dropna().iloc[-1]
regime = "above" if last["SMA_20"] > last["SMA_50"] else "at or below"
print(f"For the last API date, the 20-date SMA is {regime} the 50-date SMA.")
print(f"Sample return volatility: {analysis['Return_Pct'].std():.2f}% per observed API-date interval.")
print("These are descriptive sample statistics, not a forecast or recommendation.")"""


def notebook(slug: str, title: str, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
            "kaggle": {
                "id": f"kwaldman/{slug}",
                "title": title,
                "isInternetEnabled": True,
                "isGpuEnabled": False,
            },
            "oilpriceapi": {
                "sdkVersion": SDK_VERSION,
                "contractVersion": CONTRACT_VERSION,
                "productFactsUrl": "https://api.oilpriceapi.com/product-facts.json",
                "outputsCleared": True,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


NOTEBOOKS = {
    "01_wti_brent_spread_analysis.ipynb": notebook(
        "oilpriceapi-wti-vs-brent",
        "WTI and Brent Spread Analysis with Source Context",
        [
            markdown("spread-intro", SPREAD_INTRO),
            markdown("spread-install-heading", "## Install and execution context"),
            code("spread-install", INSTALL_CELL),
            code("spread-imports", IMPORT_CELL),
            code("spread-support", SUPPORT_SOURCE),
            markdown("spread-recovery", RECOVERY_MARKDOWN),
            code("spread-recovery-tests", RECOVERY_ASSERTIONS),
            markdown("spread-fetch-heading", "## Fetch strict API-timestamped records"),
            code("spread-fetch-helpers", FETCH_HELPERS),
            code("spread-fetch", SPREAD_FETCH),
            markdown(
                "spread-analysis-heading", "## Align API dates and calculate the spread"
            ),
            code("spread-analysis", SPREAD_ANALYSIS),
            markdown(
                "spread-chart-heading",
                "## Visualize and summarize the requested sample",
            ),
            code("spread-plot", SPREAD_PLOT),
            markdown(
                "spread-resources",
                "## Sources and limitations\n\n"
                "The latest and history requests, execution time, API timestamp field, source, currency, and unit are shown above. "
                "See the [reviewed product facts](https://api.oilpriceapi.com/product-facts.json), "
                "[API docs](https://docs.oilpriceapi.com/), and "
                "[data usage policy](https://www.oilpriceapi.com/legal/data-usage).",
            ),
        ],
    ),
    "02_oil_price_technical_analysis.ipynb": notebook(
        "oil-price-technical-analysis",
        "API-Timestamped Brent Technical Indicators",
        [
            markdown("technical-intro", TECHNICAL_INTRO),
            markdown("technical-install-heading", "## Install and execution context"),
            code("technical-install", INSTALL_CELL),
            code("technical-imports", IMPORT_CELL),
            code("technical-support", SUPPORT_SOURCE),
            markdown("technical-recovery", RECOVERY_MARKDOWN),
            code("technical-recovery-tests", RECOVERY_ASSERTIONS),
            markdown(
                "technical-fetch-heading", "## Fetch strict API-timestamped records"
            ),
            code("technical-fetch-helpers", FETCH_HELPERS),
            code("technical-fetch", TECHNICAL_FETCH),
            markdown(
                "technical-analysis-heading", "## Calculate descriptive indicators"
            ),
            code("technical-analysis", TECHNICAL_ANALYSIS),
            markdown("technical-chart-heading", "## Visualize the requested sample"),
            code("technical-plot", TECHNICAL_PLOT),
            markdown(
                "technical-resources",
                "## Sources and limitations\n\n"
                "The request method, execution time, API timestamp field, source, currency, and unit are shown above. "
                "See the [reviewed product facts](https://api.oilpriceapi.com/product-facts.json), "
                "[API docs](https://docs.oilpriceapi.com/), and "
                "[data usage policy](https://www.oilpriceapi.com/legal/data-usage).",
            ),
        ],
    ),
}


def main() -> None:
    for filename, contents in NOTEBOOKS.items():
        destination = ROOT / filename
        destination.write_text(json.dumps(contents, indent=1, ensure_ascii=True) + "\n")
        print(f"generated {destination.name}")


if __name__ == "__main__":
    main()
