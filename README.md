# OilPriceAPI Kaggle Notebooks

Reproducible, source-aware OilPriceAPI analysis notebooks. Repository copies contain no stored outputs, API keys, account responses, or customer data.

Product and access claims are governed by the [versioned OilPriceAPI product-facts contract](https://api.oilpriceapi.com/product-facts.json), reviewed 2026-07-18. Latest available values include API timestamps; cadence, history depth, and access vary by source, market hours, dataset, and account entitlement.

## Notebooks

### WTI and Brent Spread Analysis

- Repository: [01_wti_brent_spread_analysis.ipynb](01_wti_brent_spread_analysis.ipynb)
- Kaggle URL: https://www.kaggle.com/code/kwaldman/oilpriceapi-wti-vs-brent
- Method: strict latest and history GET requests, API-record-date alignment, and descriptive spread statistics

### API-Timestamped Brent Technical Indicators

- Repository: [02_oil_price_technical_analysis.ipynb](02_oil_price_technical_analysis.ipynb)
- Kaggle URL: https://www.kaggle.com/code/kwaldman/oil-price-technical-analysis
- Method: strict latest and history GET requests plus descriptive SMA, EMA, RSI, and return-volatility calculations

Both public Kaggle URLs currently require a republish receipt for this repository revision. Do not treat their displayed output as current unless the notebook shows its execution time and API timestamp fields.

## Runtime Contract

- Python package: `oilpriceapi[pandas]==1.11.0`
- Secret label: `OILPRICEAPI_KEY` through Kaggle Add-ons > Secrets
- First request: `GET /v1/prices/latest?by_code=BRENT_CRUDE_USD`
- History request: `GET /v1/prices/historical` with explicit dates and `interval=daily`
- Recovery: missing secret, 401, 402/403, 429, timeout, empty response, and malformed response fail closed with a next action

The notebooks preserve symbol, numeric value, currency, unit, source, the exact API timestamp field used, freshness when returned, requested range, method, and execution time. They do not default missing units, currencies, sources, timestamps, or values.

## Validate Locally

```bash
python3 -m pip install "oilpriceapi[pandas]==1.11.0" matplotlib seaborn
python3 scripts/generate_notebooks.py
./scripts/scan-secrets.sh
python3 -m unittest discover -s tests -v
python3 scripts/package_kaggle.py
```

The unit suite executes the exact committed notebook cells against deterministic production-shaped fixtures. A public Kaggle publish additionally requires a private Kaggle credential and an attached non-customer OilPriceAPI secret; neither belongs in this repository.

## Sources

- [Product facts](https://api.oilpriceapi.com/product-facts.json)
- [API reference](https://docs.oilpriceapi.com/api-reference/prices/latest)
- [Python SDK](https://pypi.org/project/oilpriceapi/1.11.0/)
- [Data usage policy](https://www.oilpriceapi.com/legal/data-usage)
- [Service status](https://status.oilpriceapi.com)
