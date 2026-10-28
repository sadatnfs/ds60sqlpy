# bayes-014: Pointwise predictive evaluation, PSIS and the held-out unit

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`, `bayes-011`.

## Predictive evaluation needs a held-out unit

A posterior predictive density evaluated on data used for fitting can be optimistic as a measure of future performance. Leave-one-out evaluation instead refits or approximates the posterior after removing a specified unit, then evaluates that unit's predictive density. The definition of the unit is fundamental: a row, user, cluster or time block can represent very different prediction questions.

The example compares an intercept-only normal model with a linear normal model on 12 synthetic observations. Observation scale is known, and both coefficient priors are normal. This creates an analytic refitting oracle in addition to actual PyMC sampling and ArviZ's Pareto-smoothed importance-sampling approximation.

## Worked case 1: compare PSIS with exact refitting

Both models produce pointwise log-likelihood arrays, and `az.loo` returns an estimated expected log predictive density together with Pareto-k diagnostics. Large Pareto-k values indicate unreliable importance-weight behavior for the approximation. A returned score is not automatically a trustworthy estimate merely because the function completed.

The program independently removes each observation and calculates the conjugate coefficient posterior from the remaining data. The held-out predictive distribution is normal with mean \(x_i^{\mathsf T}m_{-i}\) and variance \(\sigma^2+x_i^{\mathsf T}V_{-i}x_i\). Summing those held-out log densities gives an exact leave-one-out value for this model family.

The linear model has better exact predictive performance in the constructed relationship. The program reports each PSIS approximation error relative to the exact result and retains the warning flag and maximum Pareto k. The misspecified constant model can produce a particularly problematic approximation, demonstrating why diagnostic review must precede a model-selection interpretation.

In a general model, exact analytic refitting is unavailable. Targeted refits, a suitable alternative cross-validation design or other reviewed methods may be needed. A different estimator should be chosen because it addresses the observed problem, not because it produces a preferred model ranking.

## Worked case 2: change the predictive unit

For two outcomes sharing the same uncertain parameters, a joint posterior predictive density averages their likelihood product over the same posterior draw. Multiplying two marginal posterior predictive densities instead averages each separately. These operations generally differ:

\[
\log\mathbb E[p(y_1\mid\theta)p(y_2\mid\theta)\mid y]
\ne
\log\mathbb E[p(y_1\mid\theta)\mid y]
+\log\mathbb E[p(y_2\mid\theta)\mid y].
\]

The code calculates both quantities with stable log-sum-exp operations and checks that they are not equal. This is a dependency calculation, not a substitute for actually leaving a group out. It explains why the factorization and held-out unit must be reviewed before applying a row-wise evaluation tool.

Repeated observations from an existing user differ from observations for a new user whose latent effect has not been learned. Time forecasting differs from removing a random point in the middle of an otherwise observed series. Cross-validation must reproduce the relevant information boundary rather than defaulting to whichever factorization is easiest to obtain.

## Interpret predictive scores with uncertainty

A larger ELPD means a larger average log predictive density under the stated evaluation scheme. It does not automatically establish a practically important improvement or a causal benefit from deploying the model. Model differences, their uncertainty and the target population should be considered together.

Selecting repeatedly among many models using the same cross-validation results introduces selection. Preserve the search procedure and consider an independent final assessment where appropriate. A score for one fitted model is not automatically an unbiased evaluation of all the analyst decisions that produced it.

The demonstration uses short chains and retains imperfect diagnostics. The exact conjugate oracle is the source of its reliable comparison, while sampled PSIS values illustrate approximation behavior. Do not turn the tutorial's successful execution into a claim that every reported Monte Carlo score is suitable for a deployment decision.

## Answered scientific discussion

**Is a high Pareto k merely a warning to hide in the appendix?** It can challenge the numerical reliability of the approximation itself. Investigate influential observations, model misspecification and the need for a different evaluation computation.

**Why calculate exact leave-one-out in a small example?** It supplies an independent reference that reveals approximation error. The same discipline can be applied through targeted refits or simplified models when developing a larger Bayesian evaluation workflow.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `bayesian-cpu`.

```python
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
```

## Primary references

- [Vehtari and colleagues, LOO and WAIC](https://arxiv.org/abs/1507.04544)
- [ArviZ InferenceData-era LOO interface](https://python.arviz.org/en/v0.19.0/api/generated/arviz.loo.html)
