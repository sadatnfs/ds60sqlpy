# Day 24 — Solutions: EDA Best Practices

We follow a checklist to produce a concise EDA with visuals and document data quality issues.

Contents
- Exercise 1: EDA summary (text + visuals)
- Exercise 2: Document data quality issues and next steps

---

Exercise 1 — EDA summary
```python
import pandas as pd, seaborn as sns, matplotlib.pyplot as plt
sns.set_theme(style='whitegrid')

df = sns.load_dataset('penguins')

# Overview
print(df.info())
print(df.describe(numeric_only=True).T)
print(df.isna().mean().sort_values(ascending=False).head())

# Distributions
sns.histplot(data=df, x='body_mass_g', hue='sex', kde=True, element='step')
plt.title('Body mass by Sex'); plt.tight_layout(); plt.show()

# Relationships
sns.scatterplot(data=df, x='bill_length_mm', y='bill_depth_mm', hue='species')
plt.title('Bill length vs depth by species'); plt.tight_layout(); plt.show()

# Correlations (numeric only)
sns.heatmap(df.corr(numeric_only=True), annot=False, cmap='viridis')
plt.title('Correlation (numeric)'); plt.tight_layout(); plt.show()
```
Narrative
- Summarize key distributions and any skew
- Note segments with clear separation (e.g., species differences)
- List candidate features and questions to answer next

---

Exercise 2 — Data quality notes
Template
- Missingness: which columns; strategy (drop, impute)
- Dtypes: convert categorical columns to category; parse dates
- Duplicates/outliers: detection and treatment
- Leakage risks (if target present); split strategy

Example
```python
notes = {
    'missing': df.isna().mean().to_dict(),
    'dtype_suggestion': {'species': 'category', 'island': 'category'},
    'next_steps': ['impute flipper_length_mm with group median',
                   'derive bill_ratio = length/depth',
                   'segment visuals by island']
}
print(notes)
```
