# bayes-009: An actual PyMC regression and its diagnostic record

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-005`, `bayes-007`.

## Build a model whose variables have declared meanings

The first probabilistic-programming investigation fits a small regression using the actual prepared PyMC library. Its observation model is \(y_i\sim\mathcal N(a+bx_i,\sigma^2)\), with separate priors for intercept, slope and positive observation scale. The symbols identify distinct sources of variation: uncertainty about coefficients is different from the conditional noise represented by sigma.

The synthetic data contain 16 covariate values from minus one to one. Their outcomes follow an intercept .5 and slope 1.3 with a small deterministic perturbation. These known values provide a numerical check, but the fitted model is still an illustrative assumed likelihood. The data construction does not validate normal errors for an external dataset.

The prepared profile uses PyMC 5 and ArviZ 0.23 with the InferenceData object contract. This matters because newer ecosystem interfaces can use different result objects and method names. The course does not download or upgrade packages when a lesson opens.

## Worked case 1: fit real chains and retain diagnostics

The program creates a `pm.Model`, declares the three unknowns and attaches a normal likelihood to observed y. It then runs two serial chains, each with 120 warmup and 120 retained draws, a fixed seed and target acceptance .9. These bounded settings fit within the classroom budget. They are not a recommended production convergence budget.

The resulting posterior is an xarray-backed object with named chain and draw dimensions. The program calculates intercept and slope means and checks broad agreement with the known fixture. It also reports maximum R-hat, minimum bulk effective sample size and divergences for the sampled parameters. The reported values are observations from the actual run, not constants inserted into the tutorial.

An optional small trace plot displays both intercept chains. It is labeled as a short-chain illustration. Visual overlap is useful but does not replace rank-normalized diagnostics, tail effective sizes or Monte Carlo standard errors for the target quantity. Zero observed divergences is one diagnostic result, not proof that every relevant posterior region was explored.

## Worked case 2: generate future observations

Posterior predictive sampling draws observations conditional on each sampled parameter configuration. The output has dimensions two chains by 120 draws by 16 observed-design positions. The code checks this shape and compares the overall predictive mean with the observed mean.

That comparison is intentionally limited. A model can reproduce an average while missing variance, tails, dependence or a scientifically important subgroup. Predictive criticism should examine features chosen because they matter for the question, not only those the model fits most easily. The code exposes the full predictive array in the calculation so alternative summaries can be defined coherently.

Prediction at the observed covariate values is also different from forecasting at new covariates or evaluating held-out outcomes. The observed data helped fit the posterior. A posterior predictive check can reveal inadequacy, but it is not an unbiased estimate of a model-selection procedure's future performance.

## Read the diagnostic record carefully

R-hat compares within- and between-chain behavior through a modern transformed diagnostic, while effective sample size describes the information in correlated draws for particular summaries. A parameter's mean can have a different Monte Carlo precision from its extreme quantile. Review the quantities relevant to the decision rather than collapsing every diagnostic into one pass/fail badge.

The short demonstration can report warnings about chain count or effective sample size. Preserve them. A scientific continuation would use an appropriate longer run, inspect target-specific Monte Carlo error and investigate problematic geometry. Suppressing warnings or choosing a new seed until the output looks better is not a diagnostic strategy.

The code stores pointwise log-likelihood contributions for later evaluation. Their dimensions and observation unit matter. A log-likelihood entry for a repeated row is not automatically an independent predictive unit. The model-comparison tutorial revisits that contract before using information criteria or leave-one-out approximations.

## Answered scientific discussion

**Does the coefficient check establish a successful real-world regression?** It shows that the prepared inference path can recover a simple synthetic relationship within a broad tolerance. It does not establish correct modeling assumptions, calibrated uncertainty or transport to another population.

**What should be saved from a Bayesian run?** Save the model and data definitions, package versions, seeds, sampling configuration, actual diagnostics and the quantities used for interpretation. The classroom preserves submitted source and output receipts; a larger project should additionally retain the full posterior artifact in an explicitly managed storage workflow.

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
```

## Primary references

- [PyMC example gallery](https://www.pymc.io/projects/examples/en/latest/)
