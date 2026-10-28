# bayes-013: Posterior geometry with weakly identified predictors

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`, `statistics-learning-006`.

## Posterior geometry reflects the information in the design

Correlated predictors can make separate coefficients weakly identified even when a prediction contrast is well determined. A posterior describes that joint uncertainty. Reporting independent marginal summaries without their covariance can conceal the geometry that matters for predictions and scientific interpretation.

The synthetic design has an intercept and two nearly identical predictor columns. Their true generating slopes are two and minus 1.5, but the observed design strongly emphasizes their sum. The model uses independent standard-normal coefficient priors and known observation standard deviation .1. Those priors regularize weak directions; they are part of the model, not an invisible numerical repair.

## Worked case 1: derive the full normal posterior

With prior covariance I, design X and known observation variance \(\sigma^2\), the posterior covariance and mean are

\[
V=(I+X^{\mathsf T}X/\sigma^2)^{-1},\qquad
m=VX^{\mathsf T}y/\sigma^2.
\]

The program computes this exact conjugate oracle and fits the same model with actual PyMC sampling. It reports both coefficient means and checks broad numerical agreement. The short chains can have noticeable Monte Carlo error along a weakly identified direction, so close agreement of every printed digit is neither required nor claimed.

The posterior means of the individual slopes need not equal the data-generating slopes. The likelihood does not provide strong separate information, and the prior pulls the weak direction toward its preferred range. A correct posterior can therefore differ from a known generating parameter in one finite dataset without being a computational failure.

An independent analytic oracle is especially useful here. It separates posterior uncertainty and regularization from sampling error. If a sampled mean differs, examine Monte Carlo precision and geometry before assuming that a different number means a different statistical model.

## Worked case 2: a stable contrast inside unstable coefficients

The posterior covariance shows strong negative dependence between the two slopes. The variance of their sum is

\[
\operatorname{Var}(\beta_1+\beta_2\mid y)
=V_{11}+V_{22}+2V_{12}.
\]

Because the covariance term is negative, the sum can be much more precise than either coefficient alone. The code calculates that contrast variance from the analytic matrix and checks that it is smaller than both individual variances.

Ignoring covariance would overstate the uncertainty of this particular sum. For another contrast, ignoring covariance could understate uncertainty. The correct calculation follows the joint distribution and the target function, not a rule to add marginal interval widths or variances blindly.

The contrast is well supported near the observed relationship between predictors. Predicting a setting where one predictor changes independently of the other can require extrapolation along a weak direction. Good interpolation inside the training manifold does not establish reliable intervention or transport behavior outside it.

## Priors, scaling and computation

Coefficient priors have units. A standard-normal prior on a predictor measured in millimeters differs from the same numerical prior after measuring it in meters. Standardization can help express prior information and improve geometry, but its fitted transformation must be included in the prediction and evaluation procedure.

Strong posterior correlation can make numerical exploration inefficient. Reparameterization, orthogonal designs or an adapted metric may help. Those computational choices should preserve the intended target density. Changing the prior merely to obtain easier diagnostics changes the statistical model and should be reported as such.

Review diagnostic quantities for both individual coefficients and important contrasts. A sampler may estimate a stable prediction well while poorly characterizing a broad, scientifically relevant direction. Effective sample size and Monte Carlo error are quantity-specific, and a single average across parameters can conceal the important failure.

## Answered scientific discussion

**Does a tight posterior prediction imply precise feature effects?** No. Several coefficient combinations can generate nearly identical predictions over the observed feature relationship. The example demonstrates that distinction through an exact covariance calculation.

**Should the coefficient with the larger posterior mean be called more important?** That ignores scale, covariance, causal meaning and the target prediction population. Define the desired contrast or decision and evaluate it directly, with its uncertainty and assumptions.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `bayesian-cpu`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def sample_model(model, seed):
    import pymc as pm

    with model:
        return pm.sample(
            draws=120,
            tune=120,
            chains=2,
            cores=1,
            random_seed=seed,
            progressbar=False,
            target_accept=0.9,
            idata_kwargs={"log_likelihood": True},
        )


def diagnostics(trace, names):
    import arviz as az

    rhat = np.asarray(az.rhat(trace, var_names=names).to_array(), float)
    ess = np.asarray(az.ess(trace, var_names=names, method="bulk").to_array(), float)

    def finite_extreme(values, maximum):
        values = values[np.isfinite(values)]
        return float(values.max() if maximum else values.min()) if len(values) else None

    return dict(
        rhat_max=finite_extreme(rhat, True),
        bulk_ess_min=finite_extreme(ess, False),
        divergences=int(trace.sample_stats["diverging"].sum()),
        chains=int(trace.posterior.sizes["chain"]),
        retained_per_chain=int(trace.posterior.sizes["draw"]),
    )


def run_cases():
    import pymc as pm

    x = np.linspace(-1, 1, 20)
    design = np.c_[np.ones(20), x, x + 0.05 * np.sin(np.arange(20))]
    y = design @ np.array([0.5, 2.0, -1.5]) + 0.05 * np.cos(np.arange(20))
    sigma = 0.1
    covariance = np.linalg.inv(np.eye(3) + design.T @ design / sigma**2)
    expected = covariance @ design.T @ y / sigma**2
    with pm.Model() as model:
        beta = pm.Normal("beta", 0, 1, shape=3)
        pm.Normal("obs", pm.math.dot(design, beta), sigma, observed=y)
    trace = sample_model(model, 6013)
    actual = np.asarray(trace.posterior["beta"]).mean(axis=(0, 1))
    assert np.max(np.abs(actual - expected)) < 0.5
    sum_variance = covariance[1, 1] + covariance[2, 2] + 2 * covariance[1, 2]
    assert sum_variance < min(covariance[1, 1], covariance[2, 2])
    return dict(
        analytic_mean=expected.tolist(),
        sample_mean=actual.tolist(),
        coefficient_correlation=float(
            covariance[1, 2] / np.sqrt(covariance[1, 1] * covariance[2, 2])
        ),
        sum_sd=float(np.sqrt(sum_variance)),
        individual_sd=np.sqrt(np.diag(covariance))[1:].tolist(),
        diagnostics=diagnostics(trace, ["beta"]),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-013 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan problematic posteriors](https://mc-stan.org/docs/stan-users-guide/problematic-posteriors.html)
