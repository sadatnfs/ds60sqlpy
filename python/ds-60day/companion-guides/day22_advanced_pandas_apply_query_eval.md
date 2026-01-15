# Day 22 — Advanced Pandas: apply, pipe, query, eval (Companion Guide)

## Learning objectives
- Choose between vectorized ops, agg/transform, and apply
- Structure transformation pipelines with `pipe`
- Use `query`/`eval` for readability and potential speedups

## Why this matters
The right tool for the job keeps code expressive and fast. Overusing `apply` can hide performance issues.

## Core concepts and examples
### Prefer vectorized and built-ins
```python
# good: vectorized
df['z'] = (df['x'] - df['x'].mean()) / df['x'].std()
# avoid: row-wise apply when not needed
df['z'] = df.apply(lambda r: (r.x - df['x'].mean())/df['x'].std(), axis=1)
```

### groupby + transform vs apply
```python
df['pct_of_group'] = df['sales'] / df.groupby('region')['sales'].transform('sum')
```

### pipe for readability
```python
def standardize(d):
    cols = ['x','y']
    return d.assign(**{c: (d[c]-d[c].mean())/d[c].std() for c in cols})

out = (df
       .pipe(standardize)
       .query('region != "NA"')
      )
```

### query/eval
```python
subset = df.query('price > 100 and category in ["A","B"]')
df.eval('ratio = sales / qty', inplace=True)
```

## Common pitfalls
- Using `apply` with `axis=1` for simple arithmetic — it’s slow and obscures intent
- `eval/query` strings don’t see Python local variables unless you pass them via `@var`
- Chained indexing sneaks back in with query; use `loc` for assignment

## Practice exercises
1) Rewrite an `apply` solution using `transform` or vectorized ops
2) Build a tidy pipeline using `pipe` and `assign`
3) Use `query` with external variables via `@threshold`

## Further reading
- Method chaining and pipe: https://pandas.pydata.org/pandas-docs/stable/user_guide/enhancingperf.html#method-chaining
- eval/query: https://pandas.pydata.org/pandas-docs/stable/user_guide/enhancingperf.html#enhancing-performance-eval
