# Day 25 — Solutions: Visualization with Matplotlib & Seaborn

We recreate EDA visuals with better labeling and export figures with a consistent style.

Contents
- Exercise 1: Recreate two plots with improved labeling
- Exercise 2: Export figures under the ignored course artifact directory

---

Setup
```python
import pathlib

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(context='notebook', style='whitegrid')
FIG_DIR = pathlib.Path('artifacts/day25/figures')
FIG_DIR.mkdir(parents=True, exist_ok=True)
```

Exercise 1 — Improved labeling
```python
df = sns.load_dataset('tips')

# Histogram
fig, ax = plt.subplots(figsize=(6,4))
sns.histplot(data=df, x='total_bill', kde=True, ax=ax)
ax.set(title='Distribution of Total Bill', xlabel='Total bill ($)', ylabel='Count')
fig.tight_layout(); fig.savefig(FIG_DIR/'total_bill_hist.png', dpi=150)

# Scatter with trend
fig, ax = plt.subplots(figsize=(6,4))
sns.regplot(data=df, x='total_bill', y='tip', scatter_kws={'alpha':0.4}, ax=ax)
ax.set(title='Tip vs Total Bill', xlabel='Total bill ($)', ylabel='Tip ($)')
fig.tight_layout(); fig.savefig(FIG_DIR/'tip_vs_total_bill.png', dpi=150)
```

Exercise 2 — Consistent style export
```python
plt.style.use('seaborn-v0_8-whitegrid')
for ext in ['png','pdf']:
    (FIG_DIR/'total_bill_hist').with_suffix('.'+ext)
    (FIG_DIR/'tip_vs_total_bill').with_suffix('.'+ext)
```
Notes
- Use tight_layout to avoid cut labels
- Save both PNG and PDF for web and print
