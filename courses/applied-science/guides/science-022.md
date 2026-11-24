# science-022: Survey inclusion weights, clustering and population targets

Tutorial mode. Stage: advanced. Direct prerequisites: `statistics-005`, `statistics-008`.

## Sampling weights describe a design

A sample can deliberately over-represent some units to improve information about rare groups or reduce collection costs. An unweighted average then describes the realized sample, which may not represent the target population. Design-based reasoning uses known inclusion probabilities to account for how the sample was selected.

Let \(\pi_i\) be the probability that population unit \(i\) is included, and let \(S_i\) indicate inclusion. For a finite population total \(T=\sum_i y_i\), the Horvitz-Thompson estimator is

\[
\widehat T_{\mathrm{HT}}=\sum_i\frac{S_iy_i}{\pi_i},
\qquad
\mathbb{E}_{\mathrm{design}}[\widehat T_{\mathrm{HT}}]=\sum_i y_i.
\]

The expectation is over the sampling design, with population values held fixed. It is a different argument from treatment propensity weighting or model-based regression. Accurate first-order inclusion probabilities are enough for the unbiasedness statement, while variance estimation generally requires more information about the joint design.

## Key terms

- **Inclusion probability:** The design probability pi_i that population unit i enters the sample.
- **Horvitz-Thompson estimator:** A population total estimated by summing sampled values divided by their inclusion probabilities, unbiased under the design.
- **Design effect:** The variance inflation relative to independent sampling, 1 + (m - 1)rho for equal clusters of size m with correlation rho.
- **Primary sampling unit:** The first-stage unit, such as a cluster, that determines the effective number of independent observations.

## Worked case 1: distinguish expectation from one realized sample

The population values are 1,2,5,8, with unequal inclusion probabilities .2,.4,.5,.8. The code computes the design expectation of the weighted total and recovers 16 exactly. It then evaluates one particular realized sample containing the second and fourth units. That sample's weighted total is 15, illustrating that unbiasedness does not require every sample to equal the population value.

The program also calculates a ratio or Hajek-style weighted mean for that sample. Its denominator estimates population size through the sum of weights. Ratio estimators can improve practical behavior but do not generally inherit the exact finite-sample unbiasedness of the Horvitz-Thompson total. An attractive value in one sample is not proof of its design properties.

A zero inclusion probability means that the design supplies no information about the excluded unit for this estimator. Calibration weights or a model can add assumptions, but they cannot create a design-based observation that was never possible. The target population and sampling frame should therefore be defined together.

## Worked case 2: derive a cluster design effect

For a cluster of size \(m\) with equal unit variance and common pairwise correlation \(\rho\), the variance of the cluster total reflects both diagonal and off-diagonal covariance. Relative to independent units, the familiar equal-cluster expression is

\[
\operatorname{DEFF}=1+(m-1)\rho.
\]

With five units and correlation .3, the design effect is 2.2. The code constructs the covariance matrix explicitly and verifies that summing its entries produces the same factor. This derivation exposes the assumptions behind the formula rather than treating 2.2 as a generic penalty for clustered data.

Unequal cluster sizes, variable weights, stratification, informative sampling and different estimators can alter the design effect. A universal adjustment based only on the number of rows can be badly misleading. The relevant number of independent primary sampling units may be far smaller than the number of measured individuals.

## Carry the design into analysis

Retain strata, cluster IDs, inclusion probabilities and any replicate weights supplied by the design. Dropping them during cleaning can make a later variance calculation impossible. Missing responses introduce another mechanism: inclusion in the sample is not the same as responding to the survey, and response adjustment needs its own assumptions.

Poststratification and calibration align weighted summaries with known population totals. Their usefulness depends on the calibration variables and population information. Extreme resulting weights can increase variance, and a weighted population estimate should be checked for support and sensitivity. Do not choose calibration targets simply because they produce an appealing outcome.

Model-based and design-based analyses can both be useful. State which source of randomness and which target support the inference. A model that predicts outcomes accurately in the realized sample can still misrepresent the population if the sampling or response process is ignored.

## Answered scientific discussion

**Does a large weighted population count mean we observed that many independent people?** No. Weights represent units in the target under a design or adjustment. Precision still depends on the actual sample, dependence and estimator.

**Should all weights be normalized to mean one?** Some point estimates are invariant to a common rescaling, while totals and some variance procedures are not. Follow the estimator's definition and retain the original weight meaning and population totals.

## Worked example: Every possible sample under a two-draw design

```python
from itertools import combinations
import numpy as np

y = np.array([2.0, 4.0, 6.0, 20.0])
samples = list(combinations(range(4), 2))
p_sample = np.array([0.30, 0.10, 0.10, 0.10, 0.10, 0.30])  # design over the six pairs
pi = np.array([sum(p for s, p in zip(samples, p_sample) if i in s) for i in range(4)])
print("inclusion probabilities:", pi.round(2), " sum", pi.sum().round(2))

ht = np.array([sum(y[i] / pi[i] for i in s) for s in samples])
for s, p, est in zip(samples, p_sample, ht):
    print(f"sample {s}: probability {p:.2f}, HT total {est:7.3f}")
print(f"E[HT] = {p_sample @ ht:.3f}; true total {y.sum():.1f}")
print(f"design SD of HT = {np.sqrt(p_sample @ (ht - y.sum()) ** 2):.3f}")
```

Observed output:

```text
inclusion probabilities: [0.5 0.5 0.5 0.5]  sum 2.0
sample (0, 1): probability 0.30, HT total  12.000
sample (0, 2): probability 0.10, HT total  16.000
sample (0, 3): probability 0.10, HT total  44.000
sample (1, 2): probability 0.10, HT total  20.000
sample (1, 3): probability 0.10, HT total  48.000
sample (2, 3): probability 0.30, HT total  52.000
E[HT] = 32.000; true total 32.0
design SD of HT = 17.889
```

The design selects one of six pairs, with pairs (0,1) and (2,3) three times as likely as the others. Every unit still appears in exactly half the probability mass, so all inclusion probabilities equal 0.5 and each Horvitz-Thompson total is twice the sample sum. The six possible estimates range from 12 to 52 around a true total of 32. Weighting them by the design probabilities gives exactly 32.000, which is what unbiasedness means: an average over samples the design could have drawn. It says nothing about the one sample actually drawn. The most likely samples are the two worst: (0,1) gives 12 and (2,3) gives 52, together carrying 60 percent of the probability. The design standard deviation of 17.889 reflects that. A design that paired one small and one large unit with high probability would have the same inclusion probabilities and the same unbiased expectation but a much smaller spread, because joint inclusion probabilities, not marginal ones, determine the variance.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def run_cases():
    # Four equally-sized population cells; unequal inclusion is known by design.
    y = np.array([1.0, 2.0, 5.0, 8.0])
    pi = np.array([0.2, 0.4, 0.5, 0.8])
    expected_ht = float(np.sum(pi * y / pi))
    assert expected_ht == y.sum()
    actual_sample = np.array([0, 1, 0, 1], bool)
    ht = float(np.sum(y[actual_sample] / pi[actual_sample]))
    hajek = float(np.sum(y[actual_sample] / pi[actual_sample]) / np.sum(1 / pi[actual_sample]))
    # Cluster design effect derives from covariance, not from a universal penalty.
    cluster_size = 5
    rho = 0.3
    design_effect = 1 + (cluster_size - 1) * rho
    covariance = np.full((cluster_size, cluster_size), rho)
    np.fill_diagonal(covariance, 1)
    assert np.isclose(covariance.sum() / cluster_size, design_effect)
    return dict(
        population_total=float(y.sum()),
        expected_ht=expected_ht,
        sample_ht=ht,
        hajek_mean=hajek,
        design_effect=design_effect,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-022 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Statistics Canada, survey estimation and weighting](https://www150.statcan.gc.ca/n1/pub/12-539-x/steps-etapes/4147790-eng.htm)
