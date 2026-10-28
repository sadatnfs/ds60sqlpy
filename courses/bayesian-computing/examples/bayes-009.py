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

    x = np.linspace(-1, 1, 16)
    y = 0.5 + 1.3 * x + 0.05 * np.sin(np.arange(16))
    with pm.Model() as model:
        a = pm.Normal("a", 0, 1)
        b = pm.Normal("b", 0, 2)
        sigma = pm.HalfNormal("sigma", 0.5)
        pm.Normal("obs", a + b * x, sigma, observed=y)
    trace = sample_model(model, 6009)
    with model:
        predictive = pm.sample_posterior_predictive(
            trace, var_names=["obs"], random_seed=19, progressbar=False
        )
    slopes = np.asarray(trace.posterior["b"])
    intercepts = np.asarray(trace.posterior["a"])
    assert abs(slopes.mean() - 1.3) < 0.2 and abs(intercepts.mean() - 0.5) < 0.15
    pred = np.asarray(predictive.posterior_predictive["obs"])
    assert pred.shape == (2, 120, 16) and np.all(np.isfinite(pred))
    return dict(
        intercept_mean=float(intercepts.mean()),
        slope_mean=float(slopes.mean()),
        predictive_shape=list(pred.shape),
        observed_mean=float(y.mean()),
        predictive_mean=float(pred.mean()),
        diagnostics=diagnostics(trace, ["a", "b", "sigma"]),
        trace_a=intercepts.tolist(),
    )


def render_figure(evidence):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5, 3))
    for chain, values in enumerate(evidence["trace_a"]):
        ax.plot(values, label=f"Chain {chain + 1}", alpha=0.75)
    ax.set(
        title="Short-chain trace: inspect diagnostics too",
        xlabel="Retained draw",
        ylabel="Intercept",
    )
    ax.legend()
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-009 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
