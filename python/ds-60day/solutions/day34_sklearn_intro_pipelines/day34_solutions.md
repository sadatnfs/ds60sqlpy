# Day 34 — Solutions: scikit-learn Intro and Pipelines

We build a basic preprocessing + model pipeline, then swap models (Ridge) and inspect coefficients, emphasizing reproducibility and leak-free evaluation.

Contents
- Exercise 1: Build a pipeline (scaler + LinearRegression) with train/test split
- Exercise 2: Swap in Ridge and compare scores
- Exercise 3: Inspect coefficients and discuss the impact of scaling

---

Exercise 1 — Pipeline with scaler + LinearRegression
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

pipe = Pipeline([
    ('sc', StandardScaler()),
    ('lr', LinearRegression())
])
pipe.fit(Xtr, ytr)
score_lr = pipe.score(Xte, yte)
score_lr
```
Line-by-line
- StandardScaler is inside the Pipeline, so fit is performed only on training data
- R² score on the test split is returned by `score`

---

Exercise 2 — Swap to Ridge and compare
```python
from sklearn.linear_model import Ridge

pipe_ridge = Pipeline([
    ('sc', StandardScaler()),
    ('ridge', Ridge(alpha=1.0, random_state=42))
])
pipe_ridge.fit(Xtr, ytr)
score_ridge = pipe_ridge.score(Xte, yte)
{'linear': score_lr, 'ridge': score_ridge}
```
Notes
- Ridge adds L2 regularization which can improve generalization, especially with correlated features
- Tune `alpha` via cross-validation for best results

---

Exercise 3 — Inspect coefficients with and without scaling
```python
# With scaling
pipe.fit(Xtr, ytr)
coefs_scaled = pipe.named_steps['lr'].coef_

# Without scaling (not recommended generally for linear models)
from sklearn.linear_model import LinearRegression
lr_noscale = LinearRegression().fit(Xtr, ytr)
coefs_noscale = lr_noscale.coef_

coefs_scaled, coefs_noscale
```
Interpretation
- Coefficient magnitudes are not directly comparable across features without scaling
- Scaling stabilizes optimization and makes coefficients more interpretable (relative impact per standardized feature)

Takeaways
- Always put preprocessing inside pipelines to avoid leakage
- Try regularized models (Ridge/Lasso) and select hyperparameters via CV
