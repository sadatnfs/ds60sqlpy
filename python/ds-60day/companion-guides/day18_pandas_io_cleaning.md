# Day 18 — Pandas I/O and Data Cleaning (Companion Guide)

## Learning objectives
- Read and write CSV, Parquet, Excel; parse dates and set indexes on load
- Detect, standardize, and impute missing values
- Clean columns via rename, string ops, type conversions, and categories

## Why this matters
Most data arrives messy. Reliable, repeatable cleaning transforms are the foundation for trustworthy analysis and models.

## Mental models
- Treat I/O as schema declaration: specify dtypes, parse_dates, and index_col upfront
- Cleaning is a pipeline of pure-ish transforms that should be reproducible

## Core concepts and examples
### Reading data
```python
import pandas as pd
sales = pd.read_csv('sales.csv', parse_dates=['order_date'], dtype={'store_id':'int64'})
# Parquet is faster and typed
sales.to_parquet('sales.parquet')
fast = pd.read_parquet('sales.parquet')
```

### Column cleanup
```python
(df
 .rename(columns=str.lower)
 .rename(columns={"order id":"order_id"})
 .assign(sku=lambda d: d['sku'].str.strip().str.upper())
)
```

### Types and categories
```python
df['year'] = df['year'].astype('Int64')   # nullable integer
df['state'] = df['state'].astype('category')
```

### Missing values
```python
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['price'] = df['price'].fillna(df['price'].median())
```

### Dates and indexes
```python
df['dt'] = pd.to_datetime(df['dt'], errors='coerce', utc=True)
df = df.set_index('dt').sort_index()
```

## Common pitfalls
- Letting pandas infer everything; explicitly set dtypes to avoid object columns
- Using `inplace=True` everywhere; prefer method chaining for clarity and fewer bugs
- Mixing localized and UTC datetimes; pick UTC internally, localize on display

## Practice exercises
1) Load CSV with bad numerics; coerce and impute with median
2) Standardize a messy product code column using string vectorized ops
3) Convert high-cardinality string column to category and measure memory delta

## Stretch goals
- Write/Read compressed CSV and Parquet; compare speed/size
- Use `pd.read_csv(..., chunksize=...)` to process large files incrementally

## Check your understanding
- When would you choose Parquet over CSV?
- Why might nullable dtypes (Int64, string) be preferable to object?

## Further reading
- IO tools: https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html
- Method chaining: https://pandas.pydata.org/pandas-docs/stable/user_guide/enhancingperf.html#method-chaining
