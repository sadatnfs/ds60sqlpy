# Day 24 — Exploratory Data Analysis (EDA) Best Practices (Companion Guide)

## Learning objectives
- Systematically profile datasets and formulate hypotheses
- Visualize distributions, relationships, and segments effectively
- Avoid leakage and confirm patterns with holdouts

## Why this matters
EDA is where you learn the shape of your problem. Good habits here prevent false conclusions and wasted modeling cycles.

## Core concepts and examples
### First pass checks
```python
df.info(); df.describe(numeric_only=True)
df.isna().mean().sort_values(ascending=False).head()
```

### Distributions and relationships
- Histograms/ECDFs for skew and tails
- Boxplots/violin by category
- Scatter with trend lines; segment by hue

### Segmentation
```python
import seaborn as sns
sns.displot(df, x='amount', hue='segment', kind='kde', common_norm=False)
```

### Leakage awareness
- Perform train/test split before peeking at target-driven feature engineering
- Validate insights on the test fold

## Common pitfalls
- Overfitting your eyes: mistaking noise for signal
- Not checking data freshness, duplicates, or time gaps
- Comparing groups of very different sizes without normalization

## Practice exercises
1) Build a short EDA checklist for a new dataset
2) Visualize target vs top 3 numeric features; comment on patterns
3) Identify potential leakage features and propose mitigations

## Further reading
- statistical pitfalls: https://www.stat.cmu.edu/~cshalizi/ADAfaEPoV/
- seaborn tutorial: https://seaborn.pydata.org/tutorial.html
