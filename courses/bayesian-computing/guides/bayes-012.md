# bayes-012: Count models, exposure and overdispersion

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`.

## Counts, exposure and dispersion are different ingredients

A count model describes the number of events over a specified exposure or observation opportunity. A Poisson distribution has equal conditional mean and variance. Observed variance larger than the mean can arise from heterogeneity, dependence, zero mechanisms, varying exposure or other misspecification; it is not automatically evidence for one specific replacement family.

The example uses 12 synthetic counts whose mean is 4.5 and variance is much larger. Actual PyMC fits compare a Poisson mean model with a negative-binomial model. In the chosen parameterization, the negative-binomial conditional variance is \(\mu+\mu^2/\alpha\), where alpha is a positive dispersion parameter.

## Worked case 1: compare predictive dispersion

Both models put a prior on the log mean, then transform it to a positive mean. The negative-binomial model additionally gives alpha an exponential prior. The code samples real posterior chains and generates replicated counts at the observed design positions.

The negative-binomial predictive variance is substantially larger than the Poisson predictive variance for this fixture. Both predictive means can be close to the observed mean. That contrast demonstrates why an average alone is an inadequate predictive check for count data.

The negative-binomial construction can be understood as mixing Poisson rates under an appropriate gamma distribution. This is one possible mechanism for extra variation. It should not be treated as a literal discovery that the external population contains gamma-distributed hidden rates merely because a negative-binomial fit is convenient.

A model with extra dispersion can also absorb defects that should be addressed elsewhere, such as duplicated events or incorrectly combined exposure windows. Inspect data semantics before interpreting a flexible variance parameter as a substantive feature.

## Worked case 2: separate rate from exposure

The program checks that rate three over exposure two gives the same Poisson mean as rate 1.5 over exposure four. The likelihood depends on the product for that observation. Without a meaningful exposure definition, an estimated count mean can be misinterpreted as a rate.

In a log-link model with known exposure \(e_i\), the mean can be written \(\mu_i=e_i\exp(\eta_i)\), or \(\log\mu_i=\log e_i+\eta_i\). The log exposure is an offset with coefficient fixed at one, not an ordinary predictor whose coefficient is silently estimated. A zero exposure with a positive count is a data/model contradiction that should be investigated.

An exposure can itself be affected by an intervention or selected by observation. Adjusting for it may then change a causal question. For example, events per observed session and total events per eligible user are different targets. A statistically appropriate offset for one target does not establish the relevance of that target to the decision.

## Diagnose the count-generating process

Inspect zeros, upper tails, exposure ranges and dependence across units or time. Zero-inflated and hurdle models describe different mechanisms: one mixes a structural-zero process with a count process, while the other models zero versus positive occurrence and then the positive counts. Their parameters require interpretation and identification, particularly in a small dataset.

Posterior predictive checks should reflect the observation process and target population. Compare the fraction of zeros, maximum counts, group-specific variation and relevant time aggregation, not just a single variance. A good in-sample check still needs separate held-out evaluation when model selection or future prediction is the goal.

The short demonstration retains actual warnings and diagnostics. The counts are small enough to run offline within the classroom, but the run does not establish convergence for a large hierarchical count model. A production analysis should assess Monte Carlo precision for the particular rate, tail probability or decision quantity it will use.

## Answered scientific discussion

**Does overdispersion prove the Poisson model is useless?** It challenges a particular conditional distribution under the included predictors and exposure. A richer mean structure or dependence model can change the conclusion. The negative-binomial fit is one explicit alternative, not an automatic diagnosis.

**Why compare likelihood invariance under rate/exposure rescaling?** It checks units and interpretation independently of sampling. A model can run successfully while a data pipeline has mixed minutes, hours or different observation windows; the numerical rate then has the wrong meaning.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `bayesian-cpu`.

```python
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
```

## Primary references

- [PyMC negative-binomial distribution](https://www.pymc.io/projects/docs/en/stable/api/distributions/generated/pymc.NegativeBinomial.html)
