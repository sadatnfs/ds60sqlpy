# Day 37 — Regularization and Linear Models (Companion Guide)

## Learning objectives
- Understand bias–variance, overfitting, and the role of regularization
- Train Ridge, Lasso, and ElasticNet with proper scaling
- Use cross-validation to select alpha and interpret coefficients

## Why this matters
Regularization improves generalization and stabilizes estimates, especially with multicollinearity and high-dimensional features.

## Mental models
- Ridge (L2) shrinks coefficients continuously; Lasso (L1) can set them exactly to zero
- Stronger regularization increases bias, decreases variance; sweet spot via CV

## Core concepts and examples
```python
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.pipeline import Pipeline

alphas = [0.001, 0.01, 0.1, 1.0, 10.0]
ridge = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RidgeCV(alphas=alphas, store_cv_values=True))
])
ridge.fit(X_train, y_train)

lasso = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LassoCV(alphas=alphas, max_iter=5000, random_state=0))
])
lasso.fit(X_train, y_train)

enet = Pipeline([
    ('scaler', StandardScaler()),
    ('model', ElasticNetCV(l1_ratio=[0.2,0.5,0.8], alphas=alphas, random_state=0))
])
enet.fit(X_train, y_train)
```

### Coefficient paths (idea)
- Use sklearn.linear_model.lasso_path to visualize sparsity vs alpha

## Common pitfalls
- Skipping scaling; penalization depends on scale
- Comparing raw coefficients across differently scaled features
- Using default max_iter too low for Lasso; increase if not converged

## Practice exercises
1) Compare Ridge vs Lasso performance via CV on a noisy dataset
2) Plot coefficient paths for Lasso and discuss sparsity
3) Tune ElasticNet l1_ratio; report best alpha and l1_ratio

## Further reading
- Linear models: https://scikit-learn.org/stable/modules/linear_model.html
