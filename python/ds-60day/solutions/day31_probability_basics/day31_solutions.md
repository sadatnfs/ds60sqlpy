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

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`rng = np.random.default_rng(seed)`:** creates an isolated reproducible random-number generator; the seed is an experiment input.
2. **`rng.binomial(n, p, size)`:** returns `size` independent counts, each between zero and `n`, under constant success probability `p`.
3. **`event.mean()`:** estimates a probability only when the Boolean or 0/1 array represents the event at the intended experimental grain.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Analytic probability establishes the target; seeded simulation then measures approximation error without replacing the derivation.

**Useful alternative:** For rare-event approximations, a Poisson model can be useful when its assumptions are stated and checked.

**Trade-off:** More simulation runs reduce Monte Carlo error but do not repair a wrong probability model.

**Edge case to test:** A condition with zero observed support makes empirical conditional probability undefined, not zero.

**Evidence of correctness:** Probabilities must remain in [0, 1], analytic and seeded simulation results should agree within a stated tolerance, and every conditional estimate must report its denominator.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Simulate `Binomial(n=10, p=0.3)` 10,000 times and plot a histogram.

**How to reason about it:** A Binomial draw is a count, so the possible values are the integers 0 through n. Use integer-centered bins, a seeded generator, and compare the empirical mean and variance with n*p and n*p*(1-p); a visually smooth histogram alone does not validate the simulation.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Simulate Binomial(n=10, p=0.3) 10,000 times and plot a histogram`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then show the labeled figure and reconcile it with a numeric summary so appearance is not the only check.








### Reasoning notes for original Exercise 2

**Prompt:** Generate `Normal(0, 1)` values, compute their mean and variance, and overlay the probability density function. The standard-library formula is enough; SciPy is optional.

**How to reason about it:** A density histogram must use density=True before its height can be compared with a probability-density curve. Check the sample mean and variance numerically as well, and state whether variance uses the population convention (ddof=0) or an unbiased sample estimate.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Generate Normal(0, 1) values, compute their mean and variance, and overlay the probability de...`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Reasoning notes for original Exercise 3

**Prompt:** Given sensitivity `0.95`, specificity `0.90`, and prevalence `0.01`, compute \(P(\text{disease}\mid\text{positive})\).

**How to reason about it:** Bayes' denominator includes both true positives and false positives. Write every term with a conditional-probability label before inserting numbers; this prevents confusing specificity with the false-positive rate.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Given sensitivity 0.95, specificity 0.90, and prevalence 0.01, compute \(P(\text{disease}\mid...`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then show the formula or intermediate quantities and check the final value independently rather than trusting one library call.








### Exercise 4 — Prediction and uncertainty

**Prompt:** For an event with probability 0.002 observed in 1,000 independent trials, predict the chance of at least one occurrence, simulate it 20,000 times, and quantify Monte Carlo uncertainty.

**Reasoning before implementation:** Compute 1-(1-p)**n first. Treat each simulated experiment as one Bernoulli outcome and use sqrt(p_hat*(1-p_hat)/runs) for its standard error.

The complement is easier to model: “at least one” is one minus “zero.”
Keeping the analytic and simulated calculations separate gives an immediate
reasonableness check.

```python
import math
import numpy as np

event_probability = 0.002
trials = 1_000
runs = 20_000
expected = 1.0 - (1.0 - event_probability) ** trials

rng = np.random.default_rng(3104)
event_counts = rng.binomial(trials, event_probability, size=runs)
estimate = float(np.mean(event_counts >= 1))
monte_carlo_se = math.sqrt(estimate * (1.0 - estimate) / runs)

assert abs(estimate - expected) < 4 * monte_carlo_se
```

The four-standard-error comparison is a simulation diagnostic, not a proof
that every seeded run must match the analytic value exactly. Independence is
an assumption; clustered events would require another model.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `For an event with probability 0.002 observed in 1,000 independent trials, predict the chance...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.








### Exercise 5 — Implementation

**Prompt:** Estimate P(A|B) from two Boolean arrays without using a probability library. Return both the estimate and the denominator so a caller can judge support.

**Reasoning before implementation:** Count rows where B is true, then count rows where A and B are both true. Decide explicitly what happens when B never occurs.

Conditional probability is a ratio over the rows satisfying the condition.
Returning support prevents a precise-looking fraction based on almost no data.

```python
import numpy as np


def empirical_conditional(
    event_a: np.ndarray, event_b: np.ndarray
) -> tuple[float, int]:
    if event_a.shape != event_b.shape:
        raise ValueError("event arrays must have identical shapes")
    denominator = int(np.count_nonzero(event_b))
    if denominator == 0:
        raise ValueError("P(A|B) is undefined because B never occurs")
    numerator = int(np.count_nonzero(event_a & event_b))
    return numerator / denominator, denominator


estimate, support = empirical_conditional(
    np.array([True, False, True, True]),
    np.array([True, True, False, True]),
)
assert (estimate, support) == (2 / 3, 3)
```

Returning NaN is an alternative for vectorized reporting, but silently
returning zero would incorrectly claim evidence of no association.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Estimate P(A|B) from two Boolean arrays without using a probability library. Return both the...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 6 — Debugging and boundaries

**Prompt:** Design and test a Binomial-parameter validator. Include n=0, p=0, p=1, a negative n, a fractional n, and probabilities just outside the valid interval.

**Reasoning before implementation:** n is a nonnegative integer and p is a finite number in [0, 1]. Remember that bool is a subclass of int in Python.

The degenerate cases `n=0`, `p=0`, and `p=1` are valid; they should not be
rejected merely because their distributions have no spread.

```python
import math


def validate_binomial(n: int, p: float) -> tuple[int, float]:
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ValueError("p must be numeric")
    probability = float(p)
    if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("p must be finite and within [0, 1]")
    return n, probability


assert validate_binomial(0, 0) == (0, 0.0)
assert validate_binomial(4, 1) == (4, 1.0)
```

Use targeted exception tests for `-1`, `2.5`, `True`, `-1e-9`, `1.000000001`,
and NaN. Clipping invalid probabilities would hide upstream data errors.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Design and test a Binomial-parameter validator. Include n=0, p=0, p=1, a negative n, a fracti...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
