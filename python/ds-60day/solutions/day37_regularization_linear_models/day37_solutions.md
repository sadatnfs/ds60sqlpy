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

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Sweep `alpha` values and plot validation scores for Ridge and Lasso.

**How to reason about it:** Use a logarithmic alpha grid because meaningful penalty strengths span orders of magnitude. Reuse folds, plot uncertainty, and include an unregularized or very-weak-penalty baseline for context.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Inspect fitted coefficients and compare their sparsity. The separate solution also demonstrates Elastic Net as a useful extension.

**How to reason about it:** L1 can set coefficients exactly to zero; L2 usually shrinks all of them. Compare coefficients only after identical scaling and remember that correlated predictors can exchange weight.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Prediction

**Prompt:** Predict the coefficient and training-error behavior of Ridge as alpha moves from nearly zero to an extremely large value. Identify what happens to an unpenalized intercept.

**Reasoning before implementation:** Larger alpha increases shrinkage and bias; most standard estimators exclude the intercept from the penalty.

As alpha approaches zero, Ridge approaches ordinary least squares when that
solution is well defined. As alpha becomes very large, slope coefficients move
toward zero and training error generally rises. The intercept remains available
to represent the target mean when the estimator does not penalize it.

Validation error can have a U shape: moderate shrinkage may reduce variance,
while excessive shrinkage underfits. Confirm the estimator's intercept policy
rather than assuming every implementation uses the same objective.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 4 — Elastic Net implementation

**Prompt:** Build a scaled ElasticNetCV pipeline, state what alpha and l1_ratio control, and inspect both validation behavior and coefficient sparsity.

**Reasoning before implementation:** Scaling belongs before the estimator; l1_ratio=1 is Lasso-like and 0 is Ridge-like, while alpha controls overall penalty strength.

```python
import numpy as np
from sklearn.linear_model import ElasticNetCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

elastic = Pipeline(
    [
        ("scale", StandardScaler()),
        (
            "model",
            ElasticNetCV(
                alphas=np.logspace(-4, 1, 30),
                l1_ratio=[0.1, 0.5, 0.9, 1.0],
                cv=5,
                max_iter=20_000,
                random_state=37,
            ),
        ),
    ]
)
```

Fit only on training data, then report the selected parameters, held-out error,
and near-zero coefficient count. Selection stability across folds matters more
than presenting zeros as automatic feature discovery.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Scaling bug

**Prompt:** Fit Lasso to one feature measured in dollars and another measured in millions of dollars. Explain why the penalty treats them unfairly without scaling and repair the comparison.

**Reasoning before implementation:** The L1 penalty operates on coefficient magnitude; rescaling a feature changes the coefficient needed for the same prediction.

Without scaling, equivalent predictive effects can require coefficients with
very different numeric magnitudes, so the penalty is not comparable across
features. Place `StandardScaler` inside the pipeline before Lasso and evaluate
the complete pipeline in each fold.

If a sparse matrix is used, choose a scaler compatible with sparsity (often
`with_mean=False`) rather than densifying unexpectedly. For final
interpretation, translate standardized coefficients back carefully or explain
their standardized unit.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Stability investigation

**Prompt:** Create two highly correlated predictors, refit Lasso across several bootstrap samples, and compare selected features with Ridge predictions.

**Reasoning before implementation:** Lasso may alternate which correlated feature receives weight; Ridge often distributes weight while predictions remain similar.

Record coefficient vectors and held-out predictions for every resample.
Selection frequency exposes instability that one fitted coefficient table
hides. If two interchangeable variables are selected 55% and 45% of the time,
claiming that only one “matters” is not supported.

Elastic Net can encourage grouped behavior, and domain-driven feature grouping
can improve interpretation. Always separate predictive usefulness from causal
importance.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
