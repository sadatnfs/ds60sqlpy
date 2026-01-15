# Day 31 — Probability Basics (Companion Guide)

## Learning objectives
- Understand random variables, PMF/PDF/CDF, expectation, variance
- Common distributions: Bernoulli, Binomial, Poisson, Normal, Exponential
- Law of large numbers, Central limit theorem (intuition)

## Why this matters
Probability is the language of uncertainty and the backbone of statistical reasoning.

## Core concepts and examples
### Discrete vs continuous
- PMF vs PDF; CDF for both

### Expectation and variance
```python
import numpy as np
x = np.array([0,1])
p = np.array([0.7,0.3])
E = (x*p).sum()
Var = ((x-E)**2 * p).sum()
```

### Sampling and simulation
```python
rng = np.random.default_rng(0)
samples = rng.normal(loc=0, scale=1, size=10000)
```

## Common pitfalls
- Confusing P(A|B) with P(B|A)
- Treating dependent events as independent

## Practice exercises
1) Simulate binomial outcomes and compare to theoretical mean/var
2) Visualize CLT by summing iid variables
3) Compute tail probabilities with scipy.stats

## Further reading
- SciPy stats: https://docs.scipy.org/doc/scipy/reference/stats.html
