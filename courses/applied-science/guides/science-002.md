# science-002: Overlap, weighting and the population a result describes

Tutorial mode. Stage: beginner. Direct prerequisites: `science-001`, `statistics-science-001`.

## Positivity determines what can be learned

Weighting creates a comparison population by changing the contribution of observed units. It cannot manufacture an unobserved treatment option. Let \(e(x)=P(A=1\mid X=x)\). Identification of a population average effect requires \(0<e(x)<1\) throughout the target support, together with the other causal assumptions. **Practical overlap** asks whether the available sample actually contains useful comparisons, even when the theoretical probabilities are nonzero.

For binary treatment, an inverse-probability score is

\[
\phi_i=\frac{A_iY_i}{e(X_i)}-\frac{(1-A_i)Y_i}{1-e(X_i)}.
\]

Its average targets an additive population effect under the identification assumptions. These are probability weights attached to treatment assignment. Survey inclusion weights, censoring weights and transport weights represent different mechanisms and must be derived separately before being multiplied together.

## Worked case 1: exact balance in a finite population

The program builds 100 records across two covariate strata. Treatment probabilities are .2 and .8. Outcomes follow \(Y=1+4X+2A\), so the known intervention effect is two everywhere. The raw treated and control groups have different covariate compositions. Inverse-probability weighting nevertheless recovers two exactly because the fixture repeats each cell in its stated probability proportion.

This is an arithmetic oracle, not a finite-sample guarantee. Randomly drawn samples generally produce variation around the target. Estimating the propensity introduces another source of uncertainty. A correctly coded weight formula cannot rescue an unmeasured confounder, incorrectly recorded treatment or inconsistent outcome definition.

Inspect the largest weights and the covariate distributions that they represent. For positive weights \(w_i\), a commonly used concentration summary is

\[
n_{\mathrm{eff}}=\frac{(\sum_i w_i)^2}{\sum_i w_i^2}.
\]

It equals the actual sample size when all weights are equal. In the second numerical check, weights \([1,1,1,50]\) produce an effective size below two. Four rows therefore provide little balanced averaging. This quantity is a diagnostic of weight concentration, not a universal variance formula for every estimator or sampling design.

## Worked case 2: overlap weighting changes the target

Suppose the first stratum has population mass .8 and treatment probability .1, while the second has mass .2 and probability .6. Their treatment effects are four and one. Weighting target strata in proportion to \(p(x)e(x)(1-e(x))\) emphasizes regions where either treatment is plausible. The program compares this overlap-population effect with the original population effect and verifies that they differ.

This difference is not an estimator malfunction. The target has changed. Overlap weighting can answer a useful question about the population in clinical or operational equipoise, but it should not be presented as the original population effect with a numerical stabilization trick. Likewise, removing units with extreme estimated propensities changes the represented population. A threshold chosen after observing the desired effect is an additional analyst decision.

Clipping very large inverse weights may reduce variance while introducing bias. The tradeoff depends on which units are clipped and how their outcomes differ. Keep the unclipped and clipped analyses, the fraction of affected units, and a statement of the modified procedure. Renormalizing weights separately within treatment groups produces a different finite-sample estimator even when it approaches a similar large-sample target.

## An operational overlap review

Plot propensity distributions by treatment, but do not stop at a histogram. Examine important covariate combinations, treatment availability, extreme-weight units and weighted balance. A classifier that perfectly separates treatment groups may indicate poor overlap rather than a superior causal model. Conversely, a poorly fitted propensity model may appear to create overlap by flattening real differences.

Define a failure policy before estimating the effect. Possible responses include narrowing the target population, collecting data on missing comparisons, changing the scientific question or reporting partial identification. Returning a number for every input is not a desirable requirement when the necessary comparisons do not exist.

The program rejects probabilities of zero or one explicitly. It does not silently replace them with a small epsilon. An epsilon avoids division by zero computationally while hiding the exact scientific failure. Numerical stability and identification are separate properties.

## Answered scientific discussion

**Can outcome regression solve a positivity violation?** A fitted model can extrapolate into missing cells, but the result then relies on its extrapolation assumptions. That may be an informed modeling decision; it is not the same evidence as an observed comparison.

**Should effective sample size replace the original count in a confidence formula?** Not automatically. The estimator, estimated weights, dependence structure and design determine the uncertainty calculation. Use the concentration measure to reveal influential contributions, then derive or resample the actual analysis procedure at the correct unit.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def weighted_effect(outcome, treatment, propensity):
    y, a, e = map(lambda v: np.asarray(v, float), (outcome, treatment, propensity))
    if y.ndim != 1 or y.shape != a.shape or y.shape != e.shape or not len(y):
        raise ValueError("Outcome, treatment and propensity need matching nonempty vectors")
    if not all(np.all(np.isfinite(v)) for v in (y, a, e)) or np.any((a != 0) & (a != 1)):
        raise ValueError("Use finite outcomes, probabilities and binary treatment")
    if np.any((e <= 0) | (e >= 1)):
        raise ValueError("Both treatment possibilities must have positive probability")
    return float(np.mean(a * y / e - (1 - a) * y / (1 - e)))


def effective_n(weights):
    w = np.asarray(weights, float)
    if w.ndim != 1 or not len(w) or not np.all(np.isfinite(w)) or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("Effective size needs finite nonnegative weights and positive total")
    return float(w.sum() ** 2 / (w @ w))


def run_cases():
    # Exact population table: four treatment/covariate cells, replicated by probabilities.
    x = np.repeat([0, 0, 1, 1], [40, 10, 10, 40])
    a = np.repeat([0, 1, 0, 1], [40, 10, 10, 40])
    e = np.where(x == 0, 0.2, 0.8)
    y = 1 + 4 * x + 2 * a
    estimate = weighted_effect(y, a, e)
    weights = np.where(a == 1, 1 / e, 1 / (1 - e))
    assert np.isclose(estimate, 2)
    assert effective_n([1, 1, 1, 50]) < 2
    overlap = e * (1 - e)
    effect_by_x = np.array([4.0, 1.0])
    population = np.array([0.8, 0.2])
    prop = np.array([0.1, 0.6])
    target_weights = population * prop * (1 - prop)
    target_weights /= target_weights.sum()
    overlap_effect = float(target_weights @ effect_by_x)
    population_effect = float(population @ effect_by_x)
    assert not np.isclose(overlap_effect, population_effect)
    return dict(
        ate=estimate,
        weighted_ess=effective_n(weights),
        overlap_effect=overlap_effect,
        population_effect=population_effect,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-002 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Causal Inference: What If, author resource](https://miguelhernan.org/whatifbook)
