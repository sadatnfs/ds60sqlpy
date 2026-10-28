"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


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


def exact_normal_loo(design, outcome, prior_precision, noise_sd):
    total = 0.0
    for held in range(len(outcome)):
        keep = np.arange(len(outcome)) != held
        train = design[keep]
        covariance = np.linalg.inv(prior_precision + train.T @ train / noise_sd**2)
        mean = covariance @ train.T @ outcome[keep] / noise_sd**2
        prediction = float(design[held] @ mean)
        variance = noise_sd**2 + float(design[held] @ covariance @ design[held])
        total += float(stats.norm.logpdf(outcome[held], prediction, np.sqrt(variance)))
    return total


def run_cases():
    import arviz as az
    import pymc as pm

    x = np.linspace(-1, 1, 12)
    y = 0.5 + 2 * x + 0.1 * np.sin(np.arange(12))
    models = {}
    traces = {}
    for linear in (False, True):
        with pm.Model() as model:
            a = pm.Normal("a", 0, 1)
            mu = a + pm.Normal("b", 0, 2) * x if linear else a
            pm.Normal("obs", mu, 0.2, observed=y)
        trace = sample_model(model, 6014 + int(linear))
        name = "linear" if linear else "constant"
        traces[name] = trace
        loo = az.loo(trace, pointwise=True)
        models[name] = {
            "elpd_loo": float(loo.elpd_loo),
            "p_loo": float(loo.p_loo),
            "pareto_k_max": float(np.max(loo.pareto_k)),
            "psis_warning": bool(loo.warning),
            "exact_elpd_loo": exact_normal_loo(
                np.c_[np.ones(len(x)), x] if linear else np.ones((len(x), 1)),
                y,
                np.diag([1.0, 0.25]) if linear else np.eye(1),
                0.2,
            ),
            "diagnostics": diagnostics(trace, ["a"]),
        }
    assert models["linear"]["exact_elpd_loo"] > models["constant"]["exact_elpd_loo"]
    for result in models.values():
        result["psis_approximation_error"] = result["elpd_loo"] - result["exact_elpd_loo"]
    ll = np.asarray(traces["linear"].log_likelihood["obs"]).reshape(-1, 12)[:, :2]
    joint = float(special.logsumexp(ll.sum(axis=1)) - np.log(len(ll)))
    separate = float((special.logsumexp(ll, axis=0) - np.log(len(ll))).sum())
    assert abs(joint - separate) > 1e-7
    return dict(
        models=models,
        joint_two_observation_log_prediction=joint,
        product_of_marginal_log_predictions=separate,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-014 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
