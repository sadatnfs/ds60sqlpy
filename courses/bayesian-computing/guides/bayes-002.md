# bayes-002: Log densities, normalization and exact numerical oracles

Tutorial mode. Stage: beginner. Direct prerequisites: `bayes-001`.

## Normalize densities without losing the calculation

Probabilities and densities can be extremely small. Multiplying many likelihood terms directly can underflow to zero even when their ratios are meaningful. Bayesian computation therefore usually works with log densities. Normalization must preserve the relationship between those log values and the integration or summation measure.

For log weights \(a_j\), normalized masses are

\[
w_j=\exp\{a_j-\operatorname{logsumexp}(a)\},\qquad
\operatorname{logsumexp}(a)=m+\log\sum_j\exp(a_j-m),
\]

where \(m=\max_j a_j\). Subtracting a common constant does not change the normalized masses. This identity supplies a useful implementation test and avoids attempting to exponentiate values at their original scale.

## Key terms

- **Log density:** The logarithm of a probability or density, used so products of tiny terms become sums that do not underflow.
- **logsumexp:** The stable computation m + log sum exp(a_j - m), with m the largest log weight, of the log of a sum of exponentials.
- **Normalization:** Dividing unnormalized masses by their total so they sum or integrate to one under the stated measure.
- **Quadrature:** Numerical integration with a grid and weights; an irregular grid requires appropriate quadrature weights.
- **Exact oracle:** A conjugate, quadrature or finite-mechanism reference answer used to test a more general inference system.

## Worked case 1: compare numerical integration with an exact posterior

The prior mean is normal with mean zero and variance four. Three independent observations 1,2,3 have known variance one around that unknown mean. Combining precision gives posterior variance \((1/4+3)^{-1}=4/13\) and posterior mean \((4/13)(1+2+3)=24/13\).

The program evaluates prior plus likelihood log densities over a fine uniform grid from minus six to six. Normalized grid weights recover the analytic mean and variance within a stated numerical tolerance. This is an independent oracle for the implemented log-density expression, not merely agreement between two samplers using the same possibly incorrect model.

Because the grid spacing is constant, its common width cancels when normalized weights are used for moments. An irregular grid would require appropriate quadrature weights. Treating density values at unevenly spaced points as equally weighted masses can produce a biased numerical integral without any obvious runtime error.

The finite grid also truncates the domain. Its endpoints must be far enough into the tails for the quantity being estimated. A grid can estimate a mean reasonably while missing a rare-event tail probability. Check boundary behavior, increase resolution and domain separately, and compare against an exact answer whenever one is available.

## Worked case 2: recover meaningful ratios from underflowed values

Log weights of -45000,-45001,-45002 all exponentiate to zero in ordinary floating-point arithmetic. Their direct normalized ratio is therefore undefined. The stabilized calculation nevertheless produces finite masses summing to one and exactly matches the result after adding 45000 to every log weight.

The example separates numerical failure from a model assigning truly zero probability. Negative infinity can represent an impossible configuration, while a very negative finite log density can represent a possible but unlikely one. The normalization helper rejects an all-impossible or NaN input instead of inventing a distribution.

Stable arithmetic does not make the underlying model correct. It merely permits the intended calculation to be carried out. A perfectly stabilized objective can still use an incorrect variance, omit an observation contribution or condition on unavailable data. Numerical and scientific checks need separate evidence.

## Use exact oracles strategically

Conjugate models, low-dimensional quadrature and simulated finite mechanisms provide reference answers for testing more general inference systems. Start with a model where the expected posterior is known. Then add a feature, such as an unknown scale, a hierarchy or a nonlinear likelihood, while retaining checks on any quantities that remain tractable.

A dense grid becomes expensive in high dimensions. Its computational cost grows rapidly with the number of axes, and a rectangular grid can waste most evaluations in low-density regions. That motivates Monte Carlo methods; it does not remove the value of a small exact or quadrature test case.

Units matter in density calculations. A normal standard deviation is not a variance, and a rate is not a scale. A mistaken parameter convention can still produce a normalized distribution. The explicit posterior precision calculation here catches such mistakes because the target moments are derived independently.

## Answered scientific discussion

**Why not assert only that weights sum to one?** Almost any finite set of positive numbers can be normalized. The analytic posterior moments, shift invariance and extreme-value case check different aspects of the intended model and implementation.

**Does a close grid result prove a future complex model correct?** No. It qualifies this numerical contract. The practice of building independent reference cases transfers to more complex work, while each new likelihood and geometry requires its own review.

## Worked example: Underflow-proof grid posterior for 7000 successes in 10000 trials

```python
import numpy as np
from scipy.special import logsumexp

k, n = 7000, 10000
theta = np.linspace(0.0005, 0.9995, 2000)
log_like = k * np.log(theta) + (n - k) * np.log1p(-theta)
print(f"largest log likelihood {log_like.max():.1f}")

naive = np.exp(log_like)
print("naive sum of likelihoods:", naive.sum())
with np.errstate(invalid="ignore"):
    print("naive posterior mean:", (theta * naive).sum() / naive.sum())

w = np.exp(log_like - logsumexp(log_like))
print(f"log-sum-exp posterior mean {w @ theta:.6f}")
print(f"exact Beta(7001, 3001) mean {(k + 1) / (n + 2):.6f}")
```

Observed output:

```text
largest log likelihood -6108.6
naive sum of likelihoods: 0.0
naive posterior mean: nan
log-sum-exp posterior mean 0.699960
exact Beta(7001, 3001) mean 0.699960
```

With 10,000 trials the largest log likelihood on the grid is about \(-6108.6\), and \(e^{-6108.6}\) is far below the smallest positive double, roughly \(10^{-308}\). Every term underflows to zero, the naive sum is 0.0 and the posterior mean becomes \(0/0\), printed as nan. Nothing is wrong with the model; the failure is purely numerical. Subtracting the log-sum-exp before exponentiating rescales every weight by the same constant, so the largest becomes exactly 1 and the ratios are preserved. The normalized grid mean, 0.699960, matches the exact Beta(7001, 3001) mean \(7001/10002\) to six decimals, which is the oracle check that the grid is fine enough. With only 1,000 trials the same naive code would have survived, because \(e^{-611}\) is still representable, so a passing test on small data says little about production data. Any computation that multiplies many likelihood terms should carry log densities until the final normalized ratio.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def normalized_log_weights(log_weights):
    x = np.asarray(log_weights, float)
    if (
        x.ndim != 1
        or not len(x)
        or np.any(np.isnan(x))
        or np.any(np.isposinf(x))
        or not np.any(np.isfinite(x))
    ):
        raise ValueError(
            "Use finite or negative-infinite log weights with at least one finite value"
        )
    return np.exp(x - special.logsumexp(x))


def run_cases():
    grid = np.linspace(-6, 6, 40001)
    y = np.array([1.0, 2.0, 3.0])
    logp = stats.norm.logpdf(grid, 0, 2) + stats.norm.logpdf(y[:, None], grid[None, :], 1).sum(
        axis=0
    )
    mass = normalized_log_weights(logp)
    mean = float(grid @ mass)
    variance = float(((grid - mean) ** 2) @ mass)
    assert np.isclose(mean, 24 / 13, atol=1e-6) and np.isclose(variance, 4 / 13, atol=1e-6)
    far = np.array([-45000.0, -45001.0, -45002.0])
    stable = normalized_log_weights(far)
    assert np.exp(far).sum() == 0 and np.isclose(stable.sum(), 1)
    assert np.allclose(stable, normalized_log_weights(far + 45000))
    return dict(
        grid_mean=mean,
        analytic_mean=24 / 13,
        grid_variance=variance,
        analytic_variance=4 / 13,
        stable_extreme_weights=stable.tolist(),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-002 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [SciPy log-sum-exp reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html)
