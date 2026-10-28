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
