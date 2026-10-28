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

    y = np.array([2, 3, 2, 5, 4])
    a, b = 2 + int(y.sum()), 1 + len(y)
    with pm.Model() as model:
        rate = pm.Gamma("rate", alpha=2, beta=1)
        pm.Poisson("obs", rate, observed=y)
    trace = sample_model(model, 6015)
    rates = np.asarray(trace.posterior["rate"]).ravel()
    rng = np.random.default_rng(615)
    future = rng.poisson(rates[:, None], size=(len(rates), 100)).ravel()
    grid = np.arange(11)
    loss = lambda q, d: 4 * np.maximum(d - q, 0) + np.maximum(q - d, 0)
    empirical = np.array([loss(q, future).mean() for q in grid])
    counts = np.arange(100)
    mass = stats.nbinom.pmf(counts, a, b / (b + 1))
    exact = np.array([loss(q, counts) @ mass for q in grid])
    assert abs(float(rates.mean()) - a / b) < 0.3
    assert abs(int(empirical.argmin()) - int(exact.argmin())) <= 1
    return dict(
        sample_rate=float(rates.mean()),
        analytic_rate=a / b,
        simulation_quantity=int(grid[empirical.argmin()]),
        exact_quantity=int(grid[exact.argmin()]),
        exact_expected_cost=float(exact.min()),
        oracle_decision=int(grid[exact.argmin()]),
        simulation_decision_differs=bool(empirical.argmin() != exact.argmin()),
        simulation_policy_regret=float(exact[empirical.argmin()] - exact.min()),
        monte_carlo_max_cost_error=float(np.max(np.abs(empirical - exact))),
        diagnostics=diagnostics(trace, ["rate"]),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-015 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
