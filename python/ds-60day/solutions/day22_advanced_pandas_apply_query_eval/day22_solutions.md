# Day 22 — Solutions: Advanced Pandas (apply vs vectorize, query/eval, categoricals)

We identify a slow apply, rewrite with vectorized ops, and demonstrate memory savings from categoricals.

Contents
- Exercise 1: Replace slow apply with vectorized logic or transform
- Exercise 2: Convert high-cardinality string column to category and profile memory

---

Exercise 1 — Replace slow apply
```python
import pandas as pd
import numpy as np

# Example: compute within-group percentage without row-wise apply
np.random.seed(0)
df = pd.DataFrame({
    'region': np.random.choice(list('ABCD'), size=1000),
    'sales': np.random.randint(1, 100, size=1000)
})

# SLOW (avoid):
# df['pct'] = df.apply(lambda r: r['sales'] / df[df['region']==r['region']]['sales'].sum(), axis=1)

# FAST (vectorized with transform):
group_totals = df.groupby('region')['sales'].transform('sum')
df['pct'] = df['sales'] / group_totals

print(df.head())
```
Why it’s better
- transform broadcasts group totals back to rows; no Python loop
- Readable and scales to large data

Alternative: boolean logic with vectorization
```python
# Tip percentage without apply
df2 = pd.DataFrame({'total_bill':[10,20], 'tip':[2,5]})
df2 = df2.assign(tip_pct=df2['tip']/df2['total_bill'])
```

---

Exercise 2 — Categoricals for memory
```python
import pandas as pd
import numpy as np

n = 1_000_00  # 100k rows
cities = [f"city_{i}" for i in range(2000)]
raw = pd.DataFrame({'city': np.random.choice(cities, size=n)})

mem_before = raw['city'].memory_usage(deep=True)
raw['city'] = raw['city'].astype('category')
mem_after = raw['city'].memory_usage(deep=True)

print({"bytes_before": int(mem_before), "bytes_after": int(mem_after)})
print(raw['city'].dtype)
```
Notes
- Category compresses repeated strings; huge savings for large, repetitive columns
- Beware: category imposes a fixed vocabulary; handle unknowns when joining new data

query/eval tip
```python
th = 0.2
subset = df.query('pct > @th')      # pass local variable with @
```
