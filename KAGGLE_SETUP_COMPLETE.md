# Kaggle Notebooks - Setup Complete

## Summary

Two professional Jupyter notebooks are ready on GitHub and need to be imported to Kaggle.

**GitHub Repo**: https://github.com/OilpriceAPI/kaggle-notebooks

## Notebooks Ready

### 1. WTI vs Brent Spread Analysis
**File**: `01_wti_brent_spread_analysis.ipynb`

**Features**:
- Fetches 6 months of WTI and Brent crude data
- Calculates and visualizes price spread
- Identifies trading opportunities
- Professional charts and statistics

### 2. Oil Price Technical Analysis
**File**: `02_oil_price_technical_analysis.ipynb`

**Features**:
- Fetches 6 months of Brent crude data
- Technical indicators (SMA, EMA, RSI)
- Moving average crossovers
- Volatility analysis

## Changes Made

✅ **API Key Confirmed**: Email confirmed for `karl.waldman+admin@gmail.com`
✅ **Timeout Increased**: 120 seconds (from 30s default)
✅ **Date Range Optimized**: 180 days instead of 365 (6 months vs 1 year)
✅ **Multiple Backlinks**: Each notebook includes 5+ links to oilpriceapi.com

## Next Steps for You

### 1. Import to Kaggle (5 minutes each)

**Notebook 1:**
1. Go to https://www.kaggle.com/code
2. Click "New Notebook" → "Import Notebook"
3. Select "GitHub" tab
4. Enter: `OilpriceAPI/kaggle-notebooks/01_wti_brent_spread_analysis.ipynb`
5. Click "Import"

**Notebook 2:**
1. Repeat same process
2. Use: `OilpriceAPI/kaggle-notebooks/02_oil_price_technical_analysis.ipynb`

### 2. Add API Key Secret (30 seconds each)

In each notebook:
1. Click "Add-ons" → "Secrets"
2. Click "Add a new secret"
3. **Label**: `OILPRICEAPI_KEY`
4. **Value**: `3839c085460dd3a9dac1291f937f5a6d1740e8c668c766bc9f95e166af59cb11`
5. Click "Add"

### 3. Enable Internet & Run (2 minutes each)

1. Click "Settings" → Enable "Internet"
2. Click "Run All"
3. Wait 2-3 minutes for execution
4. Verify charts and data appear

### 4. Make Public (10 seconds each)

1. Click "Share" → "Make Public"
2. This activates the DA 70 backlinks!

### 5. Get URLs & Update README

Once public, get the URLs (format: `https://www.kaggle.com/code/kwaldman/notebook-slug`)

Then update the README:
```bash
cd /home/kwaldman/code/kaggle-notebooks
# Edit README.md to add Kaggle URLs
git add README.md
git commit -m "Add live Kaggle notebook URLs"
git push
```

## API Key Details

**Email**: karl.waldman+admin@gmail.com
**Confirmed**: ✅ Yes (2025-11-26)
**API Key**: `3839c085460dd3a9dac1291f937f5a6d1740e8c668c766bc9f95e166af59cb11`
**Rate Limit**: Unlimited (admin account)

## Known Issues

⚠️ **API Performance**: `/v1/prices/past_year` endpoint is slow (74+ seconds)
- **Issue**: https://github.com/OilpriceAPI/oilpriceapi-api/issues/608
- **Workaround**: Reduced to 180 days (6 months) in notebooks
- **Fix Needed**: Database indexing and query optimization

## Expected Results

### Week 1:
- 2 DA 70 backlinks live
- Indexed by Google
- 10-50 views

### Month 1:
- 100-500 views per notebook
- 5-10 upvotes
- 2-5 forks
- Comments from data scientists

### Month 3:
- 500-2,000 views per notebook
- Referenced in blog posts
- Potential DA +1-2 points
- Community credibility boost

## Backlinks in Each Notebook

1. https://oilpriceapi.com
2. https://oilpriceapi.com/auth/signup
3. https://docs.oilpriceapi.com
4. https://github.com/oilpriceapi/python-sdk
5. https://github.com/OilpriceAPI/kaggle-notebooks

**Total**: 10 DA 70 backlinks (5 per notebook × 2 notebooks)

## Files on GitHub

```
kaggle-notebooks/
├── README.md
├── 01_wti_brent_spread_analysis.ipynb
├── 02_oil_price_technical_analysis.ipynb
└── .gitignore
```

## Support

If notebooks fail to run:
1. Check API key is added to Secrets correctly
2. Verify "Internet" is enabled in Settings
3. Check execution logs for specific errors
4. API may be slow - wait up to 3 minutes

Ready to import! 🚀
