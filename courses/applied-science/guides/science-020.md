# science-020: Dependent effects, missing studies and synthesis sensitivity

Tutorial mode. Stage: advanced. Direct prerequisites: `science-019`.

## Multiple estimates can carry shared information

Several effects from one study may share participants, controls, instruments or outcome measurements. Treating them as independent can make the evidence appear more precise than it is. The correlation does not disappear because the estimates occupy separate spreadsheet rows.

If a vector of estimates \(\mathbf y\) shares a common mean under a specified model and has covariance \(\mathbf V\), generalized least squares gives

\[
\widehat\mu=\frac{\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf y}
{\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf{1}},\qquad
\operatorname{Var}(\widehat\mu)=
\left(\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf{1}\right)^{-1}.
\]

The covariance matrix is part of the statistical model. It must represent the dependencies and the scale of the estimates. A matrix chosen for numerical convenience should not be presented as measured sampling covariance.

## Worked case 1: retain the same mean, change the uncertainty

Two effect estimates are .4 and .6, with variance .04 each. Treating them as independent gives a mean of .5 and variance .02. When their covariance is .03, the mean remains .5 but its variance rises to .035. The code checks both exact results.

The unchanged point estimate can make the independence error easy to miss. A chart displaying only effect values would look identical under the two models, while an interval and resulting decision could change substantially. Review uncertainty calculations even when an alternative model leaves the central estimate stable.

Perfect or near-perfect dependence can make the covariance matrix singular or poorly conditioned. Two identical reported estimates do not provide two independent measurements. Possible responses include selecting a prespecified estimate, aggregating within study, using a multivariate model or applying an appropriate cluster-robust method with enough independent clusters. An arbitrary tiny diagonal jitter changes the model and should be justified rather than hidden.

## Worked case 2: make a missing-study scenario explicit

The visible effects are .3,.5,.7, giving a mean of .5. Adding two hypothetical missing effects of -.2 and -.1 lowers the arithmetic mean to .24. The program labels this as a sensitivity scenario. It does not estimate the missing studies or demonstrate that they exist.

The usefulness of the scenario depends on its interpretation. It might ask how many negative findings of a particular scale would alter a decision, or how selection could differ by study precision. A credible analysis should connect those assumptions to the review process, registration records, outcome reporting and subject-matter knowledge.

Funnel asymmetry, small-study effects and publication bias are related but distinct. Heterogeneity, measurement differences or design quality can also produce patterns associated with study size. A diagnostic plot should motivate investigation rather than automatically label every asymmetric pattern as a missing-publication mechanism.

## Organize a reproducible synthesis ledger

Use a stable study identifier and retain all candidate outcomes, their eligibility decisions and shared samples. Record how one estimate was selected when multiple versions exist. The unit resampled for uncertainty should reflect the independent evidence source; resampling individual effects from the same study as if they were independent can reproduce the original mistake.

If correlations are unknown, sensitivity analysis across scientifically plausible values may be more transparent than pretending independence. For a small number of studies, asymptotic robust-variance approximations may also be unreliable. The uncertainty procedure and the effective number of independent clusters belong in the report.

Keep observed evidence separate from imputed or hypothetical evidence. A machine-readable column identifying scenario status prevents an illustrative missing-study row from being mistaken for an extracted real result later. Likewise, preserve the difference between a study's reported standard error and one reconstructed under additional assumptions.

## Answered scientific discussion

**Can we simply average several outcomes within each study?** Sometimes that defines a meaningful composite, but the scientific target, outcome scales and within-study covariance must support the combination. Averaging is not a universal way to remove dependence.

**Does a sensitivity scenario that leaves the decision unchanged prove robustness?** It establishes stability under that stated scenario. Other selection mechanisms, stronger dependence or different effect definitions can still matter. A defensible conclusion names the alternatives examined and the assumptions left unresolved.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def gls_mean(effect, covariance):
    y = np.asarray(effect, float)
    v = np.asarray(covariance, float)
    if v.shape != (len(y), len(y)) or not np.all(np.isfinite(v)) or not np.allclose(v, v.T):
        raise ValueError("Covariance must be finite, square and symmetric")
    try:
        np.linalg.cholesky(v)
    except np.linalg.LinAlgError as error:
        raise ValueError("Covariance must be positive definite") from error
    one = np.ones(len(y))
    solve = np.linalg.solve(v, one)
    return float(solve @ y / (one @ solve)), float(1 / (one @ solve))


def run_cases():
    y = np.array([0.4, 0.6])
    independent = np.diag([0.04, 0.04])
    dependent = np.array([[0.04, 0.03], [0.03, 0.04]])
    naive = gls_mean(y, independent)
    aware = gls_mean(y, dependent)
    assert (
        naive[0] == aware[0] == 0.5 and np.isclose(naive[1], 0.02) and np.isclose(aware[1], 0.035)
    )
    visible = np.array([0.3, 0.5, 0.7])
    with_missing = np.r_[visible, [-0.2, -0.1]]
    assert with_missing.mean() < visible.mean()
    # The added effects are a stated scenario, not estimated unpublished truth.
    return dict(
        independent_variance=naive[1],
        dependent_variance=aware[1],
        published_mean=float(visible.mean()),
        sensitivity_mean=float(with_missing.mean()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-020 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Cochrane handbook, analysis and meta-analysis](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10)
