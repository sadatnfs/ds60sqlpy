# Day 28 — Solutions: Feature Engineering

We add a binned fare feature, compare scaling vs no scaling, and adjust the sklearn pipeline accordingly.

Contents
- Exercise 1: Binned fare feature
- Exercise 2: Compare scaling vs not scaling

---

Exercise 1 — Add binned fare
```python
import pandas as pd, seaborn as sns
from sklearn.preprocessing import OneHotEncoder, StandardScaler, KBinsDiscretizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Data
df = sns.load_dataset('titanic').dropna(subset=['sex','class','fare','survived'])
X = df[['sex','class','fare']]
y = df['survived']

# Add fare_binned as a feature via discretizer
pre = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['sex','class']),
    ('num', StandardScaler(), ['fare']),
    ('bin', KBinsDiscretizer(n_bins=5, encode='onehot-dense', strategy='quantile'), ['fare'])
])

pipe = Pipeline([('pre', pre), ('clf', LogisticRegression(max_iter=1000))])
pipe.fit(X,y)
acc = pipe.score(X,y)
print({'accuracy_with_bins': acc})
```

Exercise 2 — Compare with/without scaling
```python
pre_noscale = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['sex','class']),
    ('num', 'passthrough', ['fare'])
])

pipe_noscale = Pipeline([('pre', pre_noscale), ('clf', LogisticRegression(max_iter=1000))])
pipe_noscale.fit(X,y)
print({'accuracy_no_scale': pipe_noscale.score(X,y)})
```
Notes
- Scaling helps linear models when numeric ranges differ significantly
- Binning can capture non-linearities; evaluate via CV, not just resubstitution accuracy
