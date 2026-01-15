# Day 51 — Advanced Feature Engineering: Target Encoding and More (Companion Guide)

## Learning objectives
- Apply target mean encoding safely with cross-fold schemes
- Use hashing for high-cardinality categorical features
- Create group stats and interactions without leakage

## Why this matters
Categorical encodings and group statistics can unlock gains, but they’re leakage-prone if done incorrectly.

## Core concepts and examples
### Target encoding (cross-fold)
```python
import numpy as np, pandas as pd
K=5
kf = list(KFold(n_splits=K, shuffle=True, random_state=0).split(df))
enc = pd.Series(index=df.index, dtype=float)
for tr, va in kf:
    mean_map = df.iloc[tr].groupby('cat')['y'].mean()
    enc.iloc[va] = df.iloc[va]['cat'].map(mean_map)
```

### Feature hashing
```python
from sklearn.feature_extraction import FeatureHasher
fh = FeatureHasher(n_features=2**12, input_type='string')
X_hash = fh.transform(df['cat'].astype(str))
```

### Group statistics
```python
df['grp_mean'] = df.groupby('group')['y'].transform('mean')
```

## Common pitfalls
- Computing encodings on full data including validation fold
- High dimensionality explosion; control with hashing or regularization
- Data leakage from future info in time series grouping

## Practice exercises
1) Implement K-fold target encoding and compare to OHE
2) Use hashing on text-like IDs and train a linear model
3) Compute rolling group means in time order without leakage

## Further reading
- Category encoders: https://contrib.scikit-learn.org/category_encoders/
