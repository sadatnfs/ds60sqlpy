# Day 19 — GroupBy, Aggregation, Pivoting (Companion Guide)

## Learning objectives
- Summarize data with groupby-agg and transform
- Reshape with pivot_table, crosstab, and stack/unstack
- Handle MultiIndex results effectively

## Why this matters
Aggregation and reshaping are core to exploratory analysis and feature creation.

## Mental models
- groupby splits data into groups, applies aggregation, and combines results
- pivot_table is a specialized aggregation with rows/columns like a spreadsheet pivot

## Core concepts and examples
### GroupBy basics
```python
(df
 .groupby('store_id')
 .agg(revenue=('sales','sum'), orders=('order_id','nunique'))
 .reset_index()
)
```

### Multiple keys and functions
```python
aggd = df.groupby(['region','product']).agg({'sales':['sum','mean'], 'qty':'sum'})
aggd.columns = ['_'.join(c) for c in aggd.columns.to_flat_index()]
```

### transform vs agg
```python
# z-score within group
df['z'] = (df['sales'] - df.groupby('region')['sales'].transform('mean')) / \
          df.groupby('region')['sales'].transform('std')
```

### Pivoting
```python
pt = pd.pivot_table(df, index='region', columns='quarter', values='sales', aggfunc='sum', fill_value=0)
ct = pd.crosstab(df['region'], df['returned'], normalize='index')
```

### Reshaping
```python
wide = pt
long = wide.stack().rename('sales').reset_index()
```

## Common pitfalls
- Forgetting `as_index=False` or `.reset_index()` when you want a flat frame
- MultiIndex column names after multi-agg; flatten columns explicitly
- Using `apply` when a built-in `agg`/`transform` exists (faster, clearer)

## Practice exercises
1) Compute year-over-year growth by store
2) Build a pivot table of average order value by region and quarter
3) Convert a MultiIndex result back to tidy long format

## Stretch goals
- Use `Grouper(freq='M')` with datetime index for time-based groups
- Compute weighted means with custom aggregation

## Further reading
- GroupBy: https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html
- Reshaping: https://pandas.pydata.org/pandas-docs/stable/user_guide/reshaping.html
