# bayes-016: Gaussian processes and conditional versus integrated uncertainty

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`, `statistics-026`.

## A Gaussian process is a joint model over function values

A Gaussian process specifies a mean function and covariance kernel for collections of latent function values. For Gaussian observation noise and fixed kernel hyperparameters, conditional predictions can be calculated with linear algebra. This provides an exact reference for a library implementation and a clear distinction between conditional and fully integrated uncertainty.

The example uses six input positions on the unit interval, a sinusoidal synthetic signal, an exponentiated-quadratic kernel with fixed length scale .25, and observation standard deviation .1. Three new input positions receive latent-function predictions. Hyperparameters are deliberately fixed; the program does not claim to have learned their uncertainty.

## Worked case 1: match PyMC with a direct covariance calculation

Let \(K\) be the training covariance including observation noise, \(K_*\) the train-to-test covariance and \(K_{**}\) the test covariance. The conditional mean and covariance are

\[
m_*=K_*^{\mathsf T}K^{-1}y,\qquad
V_*=K_{**}-K_*^{\mathsf T}K^{-1}K_*.
\]

The implementation uses solves rather than explicitly forming an inverse for those predictions. It compares its results with actual `pm.gp.Marginal.predict` output under the declared API and parameters.

The prepared implementation adds numerical jitter to stabilize covariance calculations. The program declares that jitter explicitly and includes the same small diagonal perturbation in both its training and latent predictive covariance oracle. This detail matters: an allegedly independent comparison can fail because it compared slightly different numerical models rather than exposing a library bug. Jitter should be recorded, not hidden by an unexplained looser tolerance.

The result is a latent-function prediction. Including future observation noise would require adding the relevant noise covariance and asking the library for the corresponding prediction type. A narrow latent interval should not be labeled as an interval for a noisy future observation.

## Worked case 2: integrate over uncertain hyperparameters

A second exact calculation uses two hypothetical conditional predictive distributions with means zero and two and variance .1 each. Averaging their conditional variances gives .1, but the total mixture variance is 1.1 because the conditional means differ.

The law of total variance is

\[
\operatorname{Var}(Y\mid y)=
\mathbb E[\operatorname{Var}(Y\mid\theta,y)\mid y]
+\operatorname{Var}(\mathbb E[Y\mid\theta,y]\mid y).
\]

This illustrates the uncertainty that can be omitted by conditioning on a single length scale, amplitude or noise estimate. It is not a posterior over the actual GP hyperparameters in the first case. The example separates the general identity from a computation it has not performed.

A full Bayesian GP workflow would sample or otherwise integrate over hyperparameters and combine the resulting conditional predictions consistently. That can be computationally demanding and sensitive to identifiability. A plug-in estimate may still be useful, but its uncertainty interpretation should remain explicit.

## Model choice, scaling and validation

Kernel choice encodes assumptions about smoothness and dependence. Input units affect the meaning of a length scale; a prior appropriate for normalized time is not automatically appropriate after changing to raw seconds. A smooth kernel can extrapolate confidently under assumptions that are wrong outside the observed region.

Assess predictions at the locations and horizons that match deployment. Random holdouts inside a dense design differ from forecasts beyond the observed range or predictions in a new spatial region. Preserve the training/validation boundary when selecting kernels and hyperparameters.

Numerical conditioning can worsen when inputs are nearly duplicated or noise is very small. A stable solver, explicit jitter and a scientifically justified observation model are complementary. Increasing jitter until a matrix factorization succeeds changes the effective model; diagnose the source of near-singularity and report the numerical choices.

## Answered scientific discussion

**Does a small GP example require MCMC?** Not when hyperparameters are fixed and the Gaussian model has an analytic conditional distribution. This unit intentionally uses that tractable case as an oracle for actual library computation.

**Why distinguish conditional from integrated uncertainty?** A precise conditional prediction can be misleading when there is substantial uncertainty about the conditions. The two-component variance example makes the missing term exact and visible before a larger model makes the distinction harder to inspect.

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
```

## Primary references

- [PyMC Gaussian-process marginal prediction](https://www.pymc.io/projects/docs/en/stable/api/gp/generated/classmethods/pymc.gp.Marginal.predict.html)
