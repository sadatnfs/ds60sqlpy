# Day 25 — Visualization with Matplotlib and Seaborn (Companion Guide)

## Learning objectives
- Understand the Figure/Axes model in Matplotlib
- Create common plots and style them effectively
- Use Seaborn for statistical plots and faceting

## Why this matters
Good visuals communicate insights quickly and drive decisions.

## Core concepts and examples
### Matplotlib basics
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,4))
ax.plot(df['x'], df['y'], marker='o')
ax.set(title='Y over X', xlabel='X', ylabel='Y')
fig.tight_layout()
```

### Subplots and styling
```python
fig, axes = plt.subplots(1,2, figsize=(10,4))
axes[0].hist(df['value'], bins=30, color='C0')
axes[1].scatter(df['x'], df['y'], alpha=0.6)
plt.style.use('seaborn-v0_8-whitegrid')
```

### Seaborn
```python
import seaborn as sns
sns.set_theme(context='notebook', style='whitegrid')
sns.boxplot(data=df, x='category', y='value')
sns.lmplot(data=df, x='x', y='y', hue='segment', height=4, aspect=1.2)
```

### Faceting
```python
sns.displot(df, x='value', col='segment', kde=True, col_wrap=3)
```

## Common pitfalls
- Overplotting; use alpha, hexbin, or aggregation
- Misleading axes limits; always label and consider context
- Too many colors/hues; emphasize only what matters

## Practice exercises
1) Recreate a metric dashboard with 3 subplots
2) Use faceting to compare distributions across segments
3) Style a plot for publication: labels, legends, annotations

## Further reading
- Matplotlib tutorial: https://matplotlib.org/stable/tutorials/
- Seaborn API: https://seaborn.pydata.org/api.html
