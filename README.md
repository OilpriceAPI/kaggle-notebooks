# OilPriceAPI Kaggle Notebooks

Professional Jupyter notebooks for oil price analysis using the [OilPriceAPI Python SDK](https://github.com/oilpriceapi/python-sdk).

## Notebooks

### 1. WTI vs Brent Crude Spread Analysis

**Kaggle:** [View Notebook](https://www.kaggle.com/code/kwaldman/oilpriceapi-wti-vs-brent) ✅ LIVE

Analyzes the price differential between West Texas Intermediate (WTI) and Brent Crude oil benchmarks.

**Topics covered:**

- Historical price comparison
- Spread calculation and visualization
- Trading signal identification
- Statistical analysis

### 2. Oil Price Technical Analysis

**Kaggle:** [View Notebook](https://www.kaggle.com/code/kwaldman/oil-price-technical-analysis) ✅ LIVE

Comprehensive technical analysis with indicators and forecasting.

**Topics covered:**

- Technical indicators (SMA, EMA, RSI)
- Volatility analysis
- Moving average crossovers
- Trend detection

## Requirements

```bash
pip install oilpriceapi pandas matplotlib seaborn scipy
```

## Get API Key

Free tier includes 100 requests (lifetime):

- **Sign up:** [oilpriceapi.com/signup](https://www.oilpriceapi.com/signup?utm_source=kaggle&utm_medium=notebook&utm_campaign=readme)
- **Documentation:** [docs.oilpriceapi.com](https://docs.oilpriceapi.com)
- **Python SDK:** [github.com/oilpriceapi/python-sdk](https://github.com/oilpriceapi/python-sdk)

## Running Notebooks

### On Kaggle

1. Click notebook links above
2. Click "Copy & Edit"
3. Add your API key in Secrets (label: `OILPRICEAPI_KEY`)
4. Run all cells

### Locally

```bash
jupyter notebook notebook_name.ipynb
```

## Contributing

Issues and pull requests welcome!

## License

MIT

## Also Available As

- **[Python SDK](https://pypi.org/project/oilpriceapi/)** - The SDK used in these notebooks
- **[Node.js SDK](https://www.npmjs.com/package/oilpriceapi)** - TypeScript/JavaScript SDK
- **[OpenBB Integration](https://pypi.org/project/openbb-oilpriceapi/)** - OpenBB Platform provider

---

**Built by [OilPriceAPI](https://www.oilpriceapi.com)** - Real-time commodity price data
