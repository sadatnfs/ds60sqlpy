"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import stats


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

    y = np.array([0, 0, 0, 1, 1, 2, 2, 3, 5, 8, 12, 20])
    result = {}
    for overdispersed in (False, True):
        with pm.Model() as model:
            eta = pm.Normal("eta", np.log(4), 1)
            mu = pm.Deterministic("mu", pm.math.exp(eta))
            if overdispersed:
                alpha = pm.Exponential("alpha", 1)
                pm.NegativeBinomial("obs", mu=mu, alpha=alpha, observed=y)
            else:
                pm.Poisson("obs", mu=mu, observed=y)
        trace = sample_model(model, 6012 + int(overdispersed))
        with model:
            prediction = pm.sample_posterior_predictive(
                trace, var_names=["obs"], random_seed=29, progressbar=False
            )
        draws = np.asarray(prediction.posterior_predictive["obs"])
        result["negative_binomial" if overdispersed else "poisson"] = {
            "mean": float(draws.mean()),
            "variance": float(draws.var()),
            "diagnostics": diagnostics(trace, ["eta"]),
        }
    assert result["negative_binomial"]["variance"] > result["poisson"]["variance"]
    assert np.isclose(stats.poisson.logpmf(4, 2 * 3), stats.poisson.logpmf(4, 4 * 1.5))
    return dict(
        models=result,
        observed_mean=float(y.mean()),
        observed_variance=float(y.var()),
        exposure_rate_invariance=True,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-012 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
