# Known Issues

## Performance: Slow API Response with `interval='daily'` (Issue #609)

**Status**: Open
**Priority**: P1
**Issue**: https://github.com/OilpriceAPI/oilpriceapi-api/issues/609

### Problem

The `/v1/prices/past_year` API endpoint with `interval='daily'` parameter takes **86+ seconds** to respond when fetching a full year of data. This can cause timeouts in Kaggle notebooks (120s limit).

### Root Cause

The API aggregates 750,000+ intraday tick records into ~363 daily records using Ruby memory aggregation, which is extremely slow.

### Impact on Notebooks

- **01_wti_brent_spread_analysis.ipynb**: Fetches WTI + Brent (2 API calls × 86s = 172s) - **WILL TIMEOUT**
- **02_oil_price_technical_analysis.ipynb**: Fetches Brent only (1 API call × 86s) - **MAY TIMEOUT**

### Workaround Options

**Option 1: Reduce Date Range (Recommended)**
```python
# Change from 365 days to 180 days (6 months)
start_date = end_date - timedelta(days=180)  # Instead of 365
```

**Option 2: Increase SDK Timeout**
```python
# Increase from 120s to 240s
client = OilPriceAPI(api_key=api_key, timeout=240)
```

**Option 3: Run Locally**
- No 120s timeout limit on local machines
- May take 3-5 minutes total but will complete

### Expected Fix

Database-level aggregation using PostgreSQL `DATE_TRUNC()` will reduce response time from 86s to <2s.

Target: Complete by December 2025

### Current Notebook Status

Notebooks are configured for 365 days (1 year) to demonstrate full capabilities, but **may timeout on Kaggle**.

If you experience timeouts:
1. Reduce `days=365` to `days=180` in the date range
2. Re-run the notebook

---

Last Updated: 2025-11-26
