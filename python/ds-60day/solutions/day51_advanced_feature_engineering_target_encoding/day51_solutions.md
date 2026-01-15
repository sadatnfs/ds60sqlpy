# Day 51 — Solutions: Advanced Feature Engineering (Target Encoding, Hashing, Groups)

We implement K‑fold target encoding without leakage, feature hashing for high‑cardinality categories, and rolling group statistics in time order.

Contents
- Exercise 1: K‑fold target encoding vs one‑hot
- Exercise 2: Feature hashing for IDs
- Exercise 3: Rolling group means in time without leakage

---

Setup
```python
import numpy as np, pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from scipy import sparse
np.random.seed(0)

# Synthetic data
df = pd.DataFrame({
    'cat': np.random.choice([f'c{i}' for i in range(100)], size=5000, p=None),
    'num': np.random.randn(5000),
    'y': (np.random.rand(5000) < 0.2).astype(int)
})
```

Exercise 1 — K‑fold target encoding
```python
K=5
kf = KFold(n_splits=K, shuffle=True, random_state=0)
enc = pd.Series(index=df.index, dtype=float)
for tr, va in kf.split(df):
    mean_map = df.iloc[tr].groupby('cat')['y'].mean()
    enc.iloc[va] = df.iloc[va]['cat'].map(mean_map).fillna(df.iloc[tr]['y'].mean())

df['cat_te'] = enc

# Compare to one‑hot on a simple model
X_te = np.c_[df[['num','cat_te']].values]
enc_ohe = OneHotEncoder(handle_unknown='ignore', sparse=True)
X_ohe = sparse.hstack([df[['num']].values, enc_ohe.fit_transform(df[['cat']])])

# Single train/holdout for demo
perm = np.random.permutation(len(df))
tr, te = perm[:4000], perm[4000:]
auc_te = roc_auc_score(df['y'].iloc[te], LogisticRegression(max_iter=1000).fit(X_te[tr], df['y'].iloc[tr]).predict_proba(X_te[te])[:,1])
auc_ohe = roc_auc_score(df['y'].iloc[te], LogisticRegression(max_iter=1000).fit(X_ohe[tr], df['y'].iloc[tr]).predict_proba(X_ohe[te])[:,1])
print({'AUC_target_encoding': auc_te, 'AUC_one_hot': auc_ohe})
```
Explanation
- For each fold, compute category→mean strictly on training indices, then map to validation
- Fill unknowns with global mean from training fold
- Compare with OHE; target encoding often helps for high cardinality

---

Exercise 2 — Feature hashing
```python
from sklearn.feature_extraction import FeatureHasher
fh = FeatureHasher(n_features=2**12, input_type='string')
X_hash = fh.transform(df['cat'].astype(str))  # sparse matrix
X_num = df[['num']].values
X = sparse.hstack([X_num, X_hash])
clf = LogisticRegression(max_iter=1000).fit(X[tr], df['y'].iloc[tr])
auc_hash = roc_auc_score(df['y'].iloc[te], clf.predict_proba(X[te])[:,1])
print({'AUC_hashing': auc_hash})
```
Notes
- Hashing is stateless and memory‑safe; expect collisions but often acceptable
- Adjust n_features to control dimensionality and collision rate

---

Exercise 3 — Rolling group means in time without leakage
```python
# Add a time column and group id
T = len(df)
df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)  # shuffle to show necessity of sorting
df['ts'] = pd.date_range('2020-01-01', periods=T, freq='H')
df['group'] = np.random.choice(list('ABC'), size=T)

# Sort by group then time for leakage‑safe transforms
df = df.sort_values(['group','ts']).reset_index(drop=True)

df['grp_roll_mean_y'] = (df.groupby('group')['y']
                            .apply(lambda s: s.shift(1).rolling(24, min_periods=5).mean())
                            .reset_index(level=0, drop=True))

print(df[['group','ts','y','grp_roll_mean_y']].head(30))
```
Explanation
- shift(1) ensures the rolling window uses only past observations
- Sort by group, ts so rolling is chronological within each group
- min_periods prevents NaNs early; tune to your domain
