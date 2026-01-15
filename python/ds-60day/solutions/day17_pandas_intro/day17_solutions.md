# Day 17 — Solutions: Pandas Intro (Series, DataFrame, Index)

We solve selection and transformation tasks on the `tips` dataset.

Contents
- Exercise 1: Dinner rows average tip
- Exercise 2: Boolean column is_big_party
- Exercise 3: Sort by tip percentage descending

---

Setup
```python
import pandas as pd, seaborn as sns

df = sns.load_dataset('tips')
```

Exercise 1 — Average tip for Dinner
```python
avg_tip_dinner = df.loc[df['time'] == 'Dinner', 'tip'].mean()
print(round(avg_tip_dinner, 2))
```
Line-by-line
- Boolean mask selects Dinner rows; then select the tip column; compute mean.

Exercise 2 — is_big_party (size >= 5)
```python
df = df.assign(is_big_party=df['size'] >= 5)
# or: df.loc[:, 'is_big_party'] = df['size'] >= 5
```

Exercise 3 — Sort by tip percentage
```python
df = df.assign(tip_pct=df['tip'] / df['total_bill'])
sorted_df = df.sort_values('tip_pct', ascending=False)
sorted_df[['total_bill','tip','tip_pct']].head()
```
Notes
- Use assign for chain-friendly column creation.
- Avoid chained indexing for assignment; prefer .loc or assign.
