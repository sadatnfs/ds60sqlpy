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

    x = np.linspace(0, 1, 6)[:, None]
    y = np.sin(2 * np.pi * x[:, 0])
    test = np.array([[0.15], [0.55], [0.85]])
    length = 0.25
    noise = 0.1
    jitter = 1e-6
    with pm.Model() as model:
        gp = pm.gp.Marginal(cov_func=pm.gp.cov.ExpQuad(1, ls=length))
        gp.marginal_likelihood("obs", X=x, y=y, sigma=noise, jitter=jitter)
        mean, covariance = gp.predict(test, point={}, diag=False, jitter=jitter)
    kernel = lambda a, b: np.exp(-0.5 * ((a[:, None, 0] - b[None, :, 0]) / length) ** 2)
    k = kernel(x, x) + (noise**2 + jitter) * np.eye(len(x))
    cross = kernel(x, test)
    expected = cross.T @ np.linalg.solve(k, y)
    expected_cov = (
        kernel(test, test) - cross.T @ np.linalg.solve(k, cross) + jitter * np.eye(len(test))
    )
    assert np.allclose(mean, expected, atol=1e-6) and np.allclose(
        covariance, expected_cov, atol=1e-6
    )
    # Mixing over hyperparameters adds between-component uncertainty.
    component_means = np.array([0.0, 2.0])
    component_variances = np.array([0.1, 0.1])
    total_variance = float(component_variances.mean() + component_means.var())
    assert total_variance == 1.1
    return dict(
        prediction_mean=np.asarray(mean).tolist(),
        latent_variance=np.diag(covariance).tolist(),
        known_hyperparameters=True,
        numerical_jitter=jitter,
        mixture_total_variance=total_variance,
        conditional_variance_only=0.1,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-016 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
