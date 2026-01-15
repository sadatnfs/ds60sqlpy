# Day 32 — Solutions: Statistical Inference (Estimation & Testing)

We perform common tests, compute confidence intervals, and interpret results carefully.

Contents
- Exercise 1: One-sample and two-sample t-tests with interpretation
- Exercise 2: Confidence intervals at 90%, 95%, 99% and width comparison
- Exercise 3: Chi-square test for independence on a contingency table

---

Setup
```python
import numpy as np
from scipy import stats
rng = np.random.default_rng(0)
```

Exercise 1 — One-sample and two-sample t-tests
```python
# One-sample: is the mean different from 0?
x = rng.normal(loc=0.2, scale=1.0, size=200)
t, p = stats.ttest_1samp(x, popmean=0.0)
print({'t': t, 'p': p})
# Interpret: if p<0.05, reject H0: mean==0 at 5% level

# Two-sample Welch t-test (unequal variances)
y = rng.normal(loc=0.0, scale=1.0, size=220)
t2, p2 = stats.ttest_ind(x, y, equal_var=False)
print({'t2': t2, 'p2': p2})
```
Line-by-line
- ttest_1samp compares sample mean to popmean
- Welch t-test is safer by default when variances differ

---

Exercise 2 — Confidence intervals at multiple levels
```python
mean = x.mean(); se = x.std(ddof=1)/np.sqrt(len(x))
ci90 = (mean - 1.645*se, mean + 1.645*se)
ci95 = (mean - 1.960*se, mean + 1.960*se)
ci99 = (mean - 2.576*se, mean + 2.576*se)
print({'mean': mean, 'ci90': ci90, 'ci95': ci95, 'ci99': ci99})
```
Notes
- Higher confidence → wider interval (trade-off between certainty and precision)
- For small n or unknown variance, use t critical values; with large n, z is close

---

Exercise 3 — Chi-square test for independence
```python
import numpy as np
from scipy import stats
# Example contingency table (rows: group A/B, cols: outcome Yes/No)
table = np.array([[30, 20], [15, 35]])
chi2, pval, dof, exp = stats.chi2_contingency(table)
print({'chi2': chi2, 'p': pval, 'dof': dof})
# Interpret p: small p suggests association between group and outcome
```
Pitfalls
- p-values quantify inconsistency with H0, not effect size; report effect sizes and CIs too
- Multiple tests inflate false positives; control FDR or adjust alpha
