# Day 18 — Solutions: Pandas I/O and Cleaning

We load data with types/dates, impute missing values, and return a fully typed DataFrame.

Contents
- Exercise 1: Read CSV with parse_dates and set as index
- Exercise 2: Impute numerics with median, categoricals with mode
- Exercise 3: clean(df) returning typed DataFrame

---

Exercise 1 — Read CSV with parse_dates
```python
import pandas as pd

df = pd.read_csv('sales.csv', parse_dates=['order_date'])
df = df.set_index('order_date').sort_index()
```

Exercise 2 — Impute missing values
```python
import numpy as np

num_cols = df.select_dtypes(include=['number']).columns
cat_cols = df.select_dtypes(include=['object','category']).columns

for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
    df[c] = df[c].fillna(df[c].median())

for c in cat_cols:
    mode = df[c].mode(dropna=True)
    df[c] = df[c].fillna(mode.iat[0] if not mode.empty else '')
```

Exercise 3 — clean(df) with dtypes
```python
from typing import Mapping

def clean(df: pd.DataFrame, dtypes: Mapping[str, str] | None = None) -> pd.DataFrame:
    d = df.copy()
    # Standardize columns and types
    d = d.rename(columns=str.lower)
    if dtypes:
        for col, typ in dtypes.items():
            if col in d:
                d[col] = d[col].astype(typ)
    # Coerce numeric-like strings
    for c in d.columns:
        if d[c].dtype == 'object':
            # try numeric then datetime; keep object if both fail
            d_num = pd.to_numeric(d[c], errors='ignore')
            if d_num.dtype != 'object':
                d[c] = d_num
                continue
            d_dt = pd.to_datetime(d[c], errors='ignore', utc=True)
            if hasattr(d_dt, 'dt'):
                d[c] = d_dt
    return d
```
Notes
- Prefer method chaining in real pipelines; expanded form shown for clarity.
- Consider `convert_dtypes()` to adopt nullable dtypes.
