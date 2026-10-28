# bayes-006: Markov chains, autocorrelation and deceptive acceptance rates

Tutorial mode. Stage: beginner. Direct prerequisites: `bayes-002`.

## A Markov chain is a computational procedure

Markov chain Monte Carlo constructs dependent states whose stationary distribution is the desired target under appropriate conditions. The transition rule and its initialization determine the actual finite sequence observed. Calling a procedure MCMC does not establish that a short run has reached stationarity or explored every relevant region.

For a symmetric proposal, the Metropolis acceptance probability is

\[
\alpha(x,x')=\min\{1,\pi(x')/\pi(x)\}.
\]

The program targets a standard normal distribution and proposes a normal perturbation around the current state. It compares log probabilities, avoiding direct ratios of tiny densities. Proposal terms cancel because the proposal is symmetric; that cancellation would not apply automatically to a different proposal mechanism.

## Worked case 1: inspect a functioning but correlated chain

A proposal scale of one produces a sequence whose retained mean and variance are compatible with the known standard-normal target in this fixed numerical demonstration. The code discards an initial segment, reports acceptance and calculates lag-one correlation. The target's exact moments provide an external check on this specific example.

The retained states are correlated. Under an idealized stationary AR(1) approximation, the effective sample size for a mean is roughly \(N(1-\rho)/(1+\rho)\). The program labels this as an AR(1) approximation, not a general-purpose effective sample size calculation. Real chains can have more complicated autocorrelation, heavy tails and nonlinear dependence.

Effective sample size is quantity-specific. The chain may estimate a central mean more reliably than a tail probability. A large stored file can contain relatively little independent information for the target that matters. Modern diagnostic tools use more robust procedures than this one-lag illustration and should be inspected for the relevant summaries.

## Worked case 2: perfect acceptance with no exploration

The proposal scale is set to zero. Every proposal equals the current state, every move is accepted and the chain remains at zero. Its mean exactly matches the target mean, yet its variance is zero instead of one. The program explicitly checks this failure.

This case shows why neither a high acceptance rate nor one correct summary is sufficient evidence of successful computation. The transition kernel is degenerate and does not explore the target. A histogram concentrated at the correct mean is still the wrong distribution.

The example also explains why a universal acceptance target is inappropriate across all algorithms. Proposal scale affects both how far an attempted move travels and how often it is accepted. An algorithm can make many tiny accepted moves while mixing slowly. Hamiltonian methods use a different mechanism and need additional diagnostics such as divergences and energy behavior.

## Diagnose before interpreting

Use multiple appropriately initialized chains to compare exploration. Inspect rank-normalized split R-hat, bulk and tail effective sample sizes, Monte Carlo standard errors and relevant trace behavior in a prepared inference library. These diagnostics have assumptions and finite-sample limits; no single threshold certifies every posterior quantity.

Warmup or adaptation is used to tune an algorithm and should not be treated as ordinary retained posterior draws. Removing an arbitrary burn-in segment does not guarantee that an inadequately mixing chain becomes valid. Increasing iterations can help with Monte Carlo error but may not resolve a fundamental geometry problem or disconnected mode exploration.

Separate a coding error from a computational limitation. A wrong log density can yield a well-mixed chain for the wrong target. An exactly correct log density can yield a poorly exploring chain. Tractable targets, independent density checks and simulation-based calibration complement sampler diagnostics.

## Answered scientific discussion

**Does the functioning example prove that 3,000 iterations are sufficient in general?** No. The target is a one-dimensional normal and the program has a known oracle. A hierarchy or mixture can be much harder, even with fewer observations.

**Why keep a deliberately stuck implementation?** It is a controlled counterexample to a common diagnostic mistake. It demonstrates that the properties we wish to infer about computation must be checked through several independent observations, not inferred from a reassuring acceptance percentage.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def metropolis(step, iterations=3000, seed=6):
    rng = np.random.default_rng(seed)
    current = 0.0
    values = []
    accepted = 0
    for _ in range(iterations):
        proposal = current + rng.normal(scale=step)
        if np.log(rng.uniform()) < min(0.0, -0.5 * (proposal**2 - current**2)):
            current = proposal
            accepted += 1
        values.append(current)
    return np.asarray(values[500:]), accepted / iterations


def run_cases():
    chain, acceptance = metropolis(1.0)
    lag = float(np.corrcoef(chain[:-1], chain[1:])[0, 1])
    ar1_ess = len(chain) * (1 - lag) / (1 + lag)
    stuck, stuck_acceptance = metropolis(0.0)
    assert abs(chain.mean()) < 0.2 and 0.7 < chain.var() < 1.3
    assert stuck.mean() == 0 and stuck.var() == 0 and stuck_acceptance == 1
    assert 0 < ar1_ess < len(chain)
    return dict(
        mean=float(chain.mean()),
        variance=float(chain.var()),
        acceptance=acceptance,
        lag_one=lag,
        ar1_approximate_ess=float(ar1_ess),
        stuck_acceptance=stuck_acceptance,
        stuck_variance=float(stuck.var()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-006 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan MCMC diagnostics](https://mc-stan.org/docs/reference-manual/analysis.html)
