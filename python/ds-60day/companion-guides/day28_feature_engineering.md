# Day 28 — Feature Engineering (Companion Guide)

## Learning objectives
- Engineer numeric, categorical, and datetime features
- Scale/normalize appropriately; create interactions and binning
- Avoid leakage and document transformations

## Why this matters
Good features can outclass complex models. Systematic, leak-free engineering is a competitive advantage.

## Core concepts and examples
### Numeric transforms
- Standardize/Robust scale; log1p for skew
- Polynomial features for interactions
```python
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
X_scaled = StandardScaler().fit_transform(X)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
```

### Categorical encodings
```python
from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_cat = enc.fit_transform(df[['city']])
```

### Date/time features
```python
df['dow'] = df['dt'].dt.dayofweek
df['month'] = df['dt'].dt.month
```

### Binning
```python
pd.cut(df['age'], bins=[0,18,35,50,80], labels=False)
```

## Common pitfalls
- Leakage from target-aware transforms (e.g., on full dataset before split)
- Creating too many sparse features without regularization
- Not tracking feature lineage; use pipelines and metadata

## Practice exercises
1) Create log/standardized versions of skewed variables
2) One-hot encode categories and compare model performance
3) Generate interaction features and evaluate via CV

## Further reading
- Feature engineering: https://scikit-learn.org/stable/modules/preprocessing.html
- PolynomialFeatures: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html
