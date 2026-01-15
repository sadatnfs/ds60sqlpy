# Day 31 — Solutions: Probability Basics

We simulate common distributions, visualize convergence (LLN), and solve a simple Bayes problem.

Contents
- Exercise 1: Simulate Binomial(n=10, p=0.3) and plot histogram
- Exercise 2: Generate Normal(0,1), compute mean/var, and overlay PDF
- Exercise 3: Bayes: P(disease | positive) with given sensitivity/specificity/prevalence

---

Setup
```python
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, pi, exp
rng = np.random.default_rng(42)
```

Exercise 1 — Binomial histogram
```python
n, p, trials = 10, 0.3, 10_000
samples = rng.binomial(n=n, p=p, size=trials)

plt.figure(figsize=(6,4))
plt.hist(samples, bins=range(n+2), align='left', rwidth=0.8, color='C0', edgecolor='k')
plt.title(f'Binomial(n={n}, p={p}) — {trials} trials')
plt.xlabel('k successes'); plt.ylabel('count'); plt.tight_layout(); plt.show()

# Sanity checks against theory
emp_mean = samples.mean(); emp_var = samples.var()
th_mean = n*p; th_var = n*p*(1-p)
emp_mean, th_mean, emp_var, th_var
```
Line-by-line
- rng.binomial draws repeated binomial outcomes
- histogram shows distribution of successes 0..n
- Compare empirical mean/var to theoretical n p and n p (1-p)

---

Exercise 2 — Normal(0,1) stats and PDF overlay
```python
x = rng.normal(loc=0.0, scale=1.0, size=50_000)
mu, var = x.mean(), x.var()

# Normal PDF function (no SciPy)
def normal_pdf(z: float) -> float:
    return (1.0/sqrt(2*pi)) * exp(-(z*z)/2)

# Plot histogram and overlay PDF
import numpy as np
z = np.linspace(-4, 4, 400)
pdf = np.array([normal_pdf(t) for t in z])

plt.figure(figsize=(6,4))
plt.hist(x, bins=60, density=True, color='C2', alpha=0.4, edgecolor='none')
plt.plot(z, pdf, 'k-', lw=2, label='N(0,1) PDF')
plt.title(f'Normal(0,1) — mean={mu:.3f}, var={var:.3f}')
plt.legend(); plt.tight_layout(); plt.show()
```
Notes
- density=True scales histogram to a probability density
- For higher fidelity, use SciPy if available to get pdf directly

---

Exercise 3 — Bayes: P(disease | positive)
Given sensitivity=0.95, specificity=0.90, prevalence=0.01.
```python
sens = 0.95        # P(+|D)
spec = 0.90        # P(-|~D)
prev = 0.01        # P(D)

# Bayes theorem: P(D|+) = sens*prev / (sens*prev + (1-spec)*(1-prev))
num = sens * prev
neg_spec = 1 - spec
p_pos = sens*prev + neg_spec*(1-prev)
posterior = num / p_pos
posterior
```
Result interpretation
- With low prevalence, even a good test can have moderate PPV
- Increasing specificity improves PPV when prevalence is low
