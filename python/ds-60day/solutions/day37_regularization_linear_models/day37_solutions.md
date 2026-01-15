# Day 37 — Solutions: Regularization and Linear Models

We compare Ridge (L2) and Lasso (L1) with proper scaling, sweep alpha values, and inspect sparsity of coefficients. We also touch on ElasticNet.

Contents
- Exercise 1: Sweep alpha and plot scores (Ridge vs Lasso)
- Exercise 2: Inspect coefficients and compare sparsity
- Exercise 3: Try ElasticNet and discuss l1_ratio

---

Setup
```python
import numpy as np, matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet

X, y = load_diabetes(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
```

Exercise 1 — Alpha sweep
```python
alphas = np.logspace(-3, 2, 10)  # 0.001..100
ridge_scores, lasso_scores = [], []

for a in alphas:
    ridge = Pipeline([('sc', StandardScaler()), ('m', Ridge(alpha=a))])
    lasso = Pipeline([('sc', StandardScaler()), ('m', Lasso(alpha=a, max_iter=20000))])
    ridge_scores.append(cross_val_score(ridge, X, y, cv=5).mean())
    lasso_scores.append(cross_val_score(lasso, X, y, cv=5).mean())

plt.semilogx(alphas, ridge_scores, label='Ridge CV R2')
plt.semilogx(alphas, lasso_scores, label='Lasso CV R2')
plt.xlabel('alpha'); plt.ylabel('CV R2'); plt.legend(); plt.tight_layout(); plt.show()
```
Notes
- Stronger alpha increases bias, reduces variance; sweet spot via CV
- Lasso may need higher max_iter to converge

---

Exercise 2 — Coefficients and sparsity
```python
best_ridge = Pipeline([('sc', StandardScaler()), ('m', Ridge(alpha=1.0))]).fit(Xtr, ytr)
best_lasso = Pipeline([('sc', StandardScaler()), ('m', Lasso(alpha=0.01, max_iter=20000))]).fit(Xtr, ytr)

coef_ridge = best_ridge.named_steps['m'].coef_
coef_lasso = best_lasso.named_steps['m'].coef_

sparsity = (coef_lasso == 0).sum()
{'ridge_coefs': coef_ridge, 'lasso_coefs': coef_lasso, 'lasso_zeros': int(sparsity)}
```
Interpretation
- Ridge shrinks but rarely zeros; Lasso promotes sparsity
- Scaling is critical so the penalty treats features fairly

---

Exercise 3 — ElasticNet
```python
enet = Pipeline([('sc', StandardScaler()), ('m', ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=20000))])
s = cross_val_score(enet, X, y, cv=5).mean()
{'elasticnet_cv_r2': s}
```
Takeaways
- Use CV to pick alpha (and l1_ratio for ElasticNet)
- Inspect coefficients for stability and sparsity relative to domain knowledge
