# OilPriceAPI Kaggle Notebooks

Professional Jupyter notebooks for oil price analysis using the [OilPriceAPI Python SDK](https://github.com/oilpriceapi/python-sdk).

## Notebooks

### 1. WTI vs Brent Crude Spread Analysis
**Kaggle:** [View Notebook](https://www.kaggle.com/code/kwaldman/wti-vs-brent-crude-spread-analysis-w-oilpriceapi)

Analyzes the price differential between West Texas Intermediate (WTI) and Brent Crude oil benchmarks.

**Topics covered:**
- Historical price comparison
- Spread calculation and visualization  
- Trading signal identification
- Statistical analysis

### 2. Oil Price Technical Analysis
**Kaggle:** Coming soon

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

Free tier includes 1,000 requests/month:
- **Sign up:** [oilpriceapi.com/auth/signup](https://oilpriceapi.com/auth/signup)
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

---

**Built by [OilPriceAPI](https://oilpriceapi.com)** - Real-time commodity price data
