# Key changes needed for Notebook 1:

## OLD CODE (doesn't work):
```python
wti_data = client.get_past_year_prices(by_code='WTI_USD')
brent_data = client.get_past_year_prices(by_code='BRENT_CRUDE_USD')
```

## NEW CODE (works with SDK v1.0.1):
```python
# Method 1: Get as DataFrame directly (easiest!)
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

wti_df = client.historical.to_dataframe(
    commodity='WTI_USD',
    start=start_date,
    end=end_date,
    interval='daily'
)

brent_df = client.historical.to_dataframe(
    commodity='BRENT_CRUDE_USD',
    start=start_date,
    end=end_date,
    interval='daily'
)

# Rename columns for clarity
wti_df = wti_df[['value']].rename(columns={'value': 'WTI'})
brent_df = brent_df[['value']].rename(columns={'value': 'Brent'})

# Merge on index (date)
df = wti_df.join(brent_df, how='inner')

# Calculate spread
df['Spread'] = df['Brent'] - df['WTI']
df['Spread_Pct'] = (df['Spread'] / df['WTI']) * 100

print(f"✅ Loaded {len(df)} days of data")
```

This uses the SDK's built-in `to_dataframe()` method which handles all the API calls and conversion automatically!
