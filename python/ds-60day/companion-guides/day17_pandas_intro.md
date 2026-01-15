# Day 17 — Pandas Intro: Series, DataFrame, Index (Companion Guide)

## Learning objectives
- Create Series and DataFrames; understand index, columns, and dtypes
- Select, filter, and assign data idiomatically without chained indexing
- Leverage vectorized ops, alignment, and missing-data handling

## Why this matters
Pandas is the standard table abstraction in Python data work. Mastering selection and assignment patterns early prevents subtle bugs later and speeds up every downstream task.

## Mental models
- DataFrame = ordered dict of equal-length Series sharing the same index
- Index is a labeled axis enabling alignment; it is data, not just row numbers
- Most operations are vectorized and align on index/columns automatically

## Core concepts and examples
### Creating objects
```python
import pandas as pd
s = pd.Series([10, 20, 30], name='value', index=['a','b','c'])
df = pd.DataFrame({
    'city': ['NY','SF','LA'],
    'temp_c': [8.0, 12.5, 18.3],
    'rain_mm': [5, 0, 12]
}, index=[101,102,103])
```

### Inspecting
```python
df.shape, df.dtypes, df.head(), df.tail(), df.sample(5, random_state=0)
df.info()
df.describe(numeric_only=True)
```

### Selection (avoid chained indexing)
```python
# column(s)
df['temp_c']              # Series
df[['temp_c','rain_mm']]  # DataFrame

# row(s) by label vs position
df.loc[101]                # label-based
df.iloc[0]                  # position-based

# boolean filtering
hot = df[df['temp_c'] > 15]

# assignment — use .loc for clarity
df.loc[df['temp_c'] > 10, 'comfort'] = 'ok'
```

### Alignment and arithmetic
```python
s1 = pd.Series({'a': 1, 'b': 2, 'c': 3})
s2 = pd.Series({'b': 10, 'c': 20, 'd': 30})
s1 + s2     # aligns on index; missing gives NaN
```

### Missing data
```python
df.isna().sum()
df['rain_mm'] = df['rain_mm'].astype('float')
df['rain_mm'] = df['rain_mm'].fillna(0.0)
```

## Common pitfalls
- Chained indexing like `df[df.x>0]['y'] = 1` — may not set values; use `.loc[mask, 'y'] = 1`
- Silent dtype coercion (object vs numeric); explicitly `astype` when needed
- Assuming row order equals meaning; use indexes/keys, not positions

## Practice exercises
1) Load a small CSV to a DataFrame; compute a new column from two numeric columns
2) Select top-k rows by a metric and show only selected columns
3) Demonstrate alignment by adding two Series with different indexes

## Stretch goals
- Use `pd.Categorical` for low-cardinality string columns and compare memory
- Explore `convert_dtypes()` to get nullable dtypes

## Check your understanding
- When should you prefer `.loc` over bracket selection?
- How does alignment affect arithmetic across Series/DataFrames?

## Further reading
- 10 minutes to pandas: https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
- Indexing basics: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
