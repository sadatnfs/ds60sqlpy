# Day 21 — Time Series with Pandas (Companion Guide)

## Learning objectives
- Work with datetime dtypes, indexes, time zones
- Resample, roll, and window functions
- Time-based selection and period arithmetic

## Why this matters
Time is a first-class dimension in many analyses. Pandas offers rich tools for temporal data that simplify complex logic.

## Core concepts and examples
### Datetime handling
```python
s = pd.to_datetime(df['timestamp'], utc=True)
df = df.assign(ts=s).set_index('ts').sort_index()
df.tz_convert('America/Los_Angeles')
```

### Time-based selection
```python
df.loc['2024-01']          # month
df.loc['2024-01-15']       # day
```

### Resampling and rolling
```python
# resample to daily sum
daily = df['value'].resample('D').sum()
# 7-day moving average
df['ma7'] = df['value'].rolling(window=7, min_periods=1).mean()
```

### Periods vs timestamps
```python
p = pd.PeriodIndex(['2024Q1','2024Q2'], freq='Q')
```

## Common pitfalls
- Mixing naive and tz-aware datetimes; pick UTC internally
- Using `rolling` on unsorted indexes; always sort by time
- Expecting `resample` on non-datetime index; set a DatetimeIndex first

## Practice exercises
1) Convert a column to UTC and to a local timezone for reporting
2) Compute weekly revenue and a 4-week rolling average
3) Use `asfreq` to fill a regular grid and forward-fill missing observations

## Further reading
- Timeseries: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
