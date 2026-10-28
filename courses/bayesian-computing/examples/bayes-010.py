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

    group = np.repeat(np.arange(3), [2, 8, 25])
    y = np.r_[[-3.0, -2.0], np.linspace(-0.6, 0.6, 8), np.linspace(0.6, 1.4, 25)]
    traces = {}
    for noncentered in (False, True):
        with pm.Model() as model:
            mu = pm.Normal("mu", 0, 1)
            tau = pm.HalfNormal("tau", 1)
            if noncentered:
                z = pm.Normal("z", 0, 1, shape=3)
                theta = pm.Deterministic("theta", mu + tau * z)
            else:
                theta = pm.Normal("theta", mu, tau, shape=3)
            pm.Normal("obs", theta[group], 1, observed=y)
        traces["noncentered" if noncentered else "centered"] = sample_model(
            model, 6010 + int(noncentered)
        )
    means = {
        k: np.asarray(v.posterior["theta"]).mean(axis=(0, 1)).tolist() for k, v in traces.items()
    }
    assert all(np.all(np.isfinite(m)) for m in means.values())
    oracle = np.array([2 * (-2.5) / 3, 0.0, 25 / 26])
    assert oracle[0] > -2.5 and oracle[2] < 1
    # Density identity includes the Jacobian dtheta/dz=tau in each dimension.
    mu, tau = 0.3, 1.4
    z = np.array([-0.5, 0.2, 1.0])
    theta = mu + tau * z
    centered = float(stats.norm.logpdf(theta, mu, tau).sum())
    noncentered = float(stats.norm.logpdf(z).sum())
    assert np.isclose(centered + 3 * np.log(tau), noncentered)
    return dict(
        posterior_group_means=means,
        known_hyperparameter_oracle=oracle.tolist(),
        diagnostics={k: diagnostics(v, ["mu", "tau", "theta"]) for k, v in traces.items()},
        mean_difference_max=float(
            np.max(np.abs(np.asarray(means["centered"]) - means["noncentered"]))
        ),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-010 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
