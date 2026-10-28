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

    y = np.r_[np.linspace(-0.3, 0.3, 8), 8.0]
    traces = {}
    for robust in (False, True):
        with pm.Model() as model:
            mu = pm.Normal("mu", 0, 2)
            sigma = pm.HalfNormal("sigma", 2)
            if robust:
                pm.StudentT("obs", nu=4, mu=mu, sigma=sigma, observed=y)
            else:
                pm.Normal("obs", mu, sigma, observed=y)
        traces["student_t" if robust else "normal"] = sample_model(model, 6011 + int(robust))
    means = {name: float(trace.posterior["mu"].mean()) for name, trace in traces.items()}
    assert abs(means["student_t"]) < abs(means["normal"])
    normal_penalty = float(stats.norm.logpdf(8, 0, 1) - stats.norm.logpdf(0, 0, 1))
    t_penalty = float(stats.t.logpdf(8, df=4) - stats.t.logpdf(0, df=4))
    assert t_penalty > normal_penalty
    return dict(
        location_means=means,
        normal_log_density_change=normal_penalty,
        student_log_density_change=t_penalty,
        diagnostics={k: diagnostics(v, ["mu", "sigma"]) for k, v in traces.items()},
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-011 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
