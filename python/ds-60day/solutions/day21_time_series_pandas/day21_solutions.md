# Day 21 — Solutions: Time Series with Pandas

We work through business-day series with weekly sums, and time zone handling with conversion to UTC.

Contents
- Exercise 1: Business-day time series and weekly sums
- Exercise 2: Add a time zone to a timestamp column and convert to UTC

---

Exercise 1 — Business-day series and weekly sums
```python
import pandas as pd
import numpy as np

# 1) Business-day DatetimeIndex (BDay frequency)
rng = pd.bdate_range('2024-01-01', periods=20)   # business days only

# 2) Create a Series indexed by business days
s = pd.Series(np.arange(len(rng)), index=rng, name='value')

# 3) Resample to weekly sums (W-FRI or W-SUN; pick one and be consistent)
weekly_sum = s.resample('W-FRI').sum()  # week ending Friday

print(s.head())
print(weekly_sum)
```
Line-by-line
- pd.bdate_range gives business days; weekends omitted
- resample requires a DatetimeIndex; choose an anchor (e.g., week ending Friday)

Notes
- If you want calendar weeks regardless of business days, resample still works; missing weekend days are simply absent
- For different anchors: 'W-MON', 'W-SUN', 'W-FRI', etc.

---

Exercise 2 — Time zones and UTC conversion
```python
import pandas as pd

# Example DataFrame with naive timestamps (no tz info)
df = pd.DataFrame({'ts': ['2024-02-01 08:30:00', '2024-02-01 15:45:00'],
                   'value': [10, 20]})

# 1) Parse to timezone-aware timestamps in a local zone (e.g., America/Los_Angeles)
df['ts'] = pd.to_datetime(df['ts']).dt.tz_localize('America/Los_Angeles')

# 2) Convert to UTC for storage/processing
df_utc = df.assign(ts=df['ts'].dt.tz_convert('UTC'))

# 3) Set as index and resample hourly (example)
by_hour = df_utc.set_index('ts').sort_index().resample('h').sum()

print(df)
print(df_utc)
print(by_hour.head())
```
Why this pattern
- Localize first when timestamps are local but naive
- Convert to UTC internally to avoid ambiguity (DST issues); convert back on display

Pitfalls
- Don’t .tz_localize when timestamps already have tz; use .tz_convert instead
- Always sort by time before resample/rolling
