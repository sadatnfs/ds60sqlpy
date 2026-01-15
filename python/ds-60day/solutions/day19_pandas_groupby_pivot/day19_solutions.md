# Day 19 — Solutions: GroupBy, Aggregation, Pivoting

We summarize, reshape, and validate totals on the tips dataset.

Contents
- Exercise 1: Revenue and avg tip by (day, smoker)
- Exercise 2: Pivot of average tip by (day x time) with fill_value=0
- Exercise 3: Melt wide → long, then groupby to validate totals

---

Setup
```python
import pandas as pd, numpy as np, seaborn as sns

df = sns.load_dataset('tips')
```

Exercise 1 — Group by (day, smoker)
```python
df = df.assign(revenue=df['total_bill'])    # treat total_bill as revenue here
agg = (df
    .groupby(['day','smoker'], as_index=False)
    .agg(revenue=('revenue','sum'), avg_tip=('tip','mean'))
)
agg.head()
```

Exercise 2 — Pivot avg tip by (day x time)
```python
pt = pd.pivot_table(df, values='tip', index='day', columns='time', aggfunc='mean', fill_value=0)
pt
```

Exercise 3 — Melt back to long and validate
```python
long = pt.reset_index().melt(id_vars='day', var_name='time', value_name='avg_tip')
# Validate: join with counts per (day,time) and compare weighted average to original groupby
counts = df.groupby(['day','time']).size().rename('n')
joined = (long.set_index(['day','time'])
              .join(counts)
              .reset_index())
```
Notes
- Use as_index=False or reset_index() to keep flat DataFrames when needed.
- After multi-agg, flatten columns with map or to_flat_index.
