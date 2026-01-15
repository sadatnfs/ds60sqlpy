# Day 32 — Statistical Inference: Estimation and Testing (Companion Guide)

## Learning objectives
- Confidence intervals and hypothesis testing
- t-tests, proportions tests, nonparametric alternatives
- p-values, effect sizes, and power (intuition)

## Why this matters
Inference quantifies uncertainty and guards against fooling ourselves.

## Core concepts and examples
### Confidence intervals
```python
import numpy as np, scipy.stats as st
x = rng.normal(0,1, size=100)
ci = st.t.interval(alpha=0.95, df=len(x)-1, loc=x.mean(), scale=st.sem(x))
```

### t-test
```python
st.ttest_ind(x, y, equal_var=False)
```

### Proportions
```python
from statsmodels.stats.proportion import proportions_ztest
count = np.array([45, 30]); nobs = np.array([100, 80])
proportions_ztest(count, nobs)
```

## Common pitfalls
- Overreliance on p<0.05; consider effect sizes and CIs
- Multiple comparisons without correction

## Practice exercises
1) Compute a 95% CI for a mean and interpret it
2) Compare two groups with t-test and report effect size
3) Perform a proportions test and visualize uncertainty

## Further reading
- Statsmodels: https://www.statsmodels.org
- Multiple testing: https://en.wikipedia.org/wiki/Multiple_comparisons_problem
