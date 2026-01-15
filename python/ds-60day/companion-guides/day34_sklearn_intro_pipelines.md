# Day 34 — scikit-learn Intro and Pipelines (Companion Guide)

## Learning objectives
- Understand estimators, transformers, fit/transform/predict
- Build robust Pipelines and ColumnTransformers
- Perform train/validation splits reproducibly

## Why this matters
Pipelines make preprocessing and modeling reproducible and leak-free.

## Core concepts and examples
### Basic pipeline
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

num = ['age','income']; cat = ['city']
pre = ColumnTransformer([
    ('num', StandardScaler(), num),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat)
])
clf = Pipeline([('pre', pre), ('model', LogisticRegression(max_iter=1000))])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
clf.fit(X_train, y_train)
```

## Common pitfalls
- Fitting scalers/encoders outside the pipeline (leakage)
- Not stratifying classification splits
- Forgetting to set random_state for reproducibility

## Practice exercises
1) Build a pipeline mixing numeric scaling and categorical OHE
2) Evaluate baseline accuracy and calibration
3) Persist the trained pipeline with joblib

## Further reading
- Pipeline: https://scikit-learn.org/stable/modules/compose.html
