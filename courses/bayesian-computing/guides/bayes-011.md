# bayes-011: Robust likelihoods and predictive criticism

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`.

## Robustness begins with an observation model

A normal likelihood penalizes large residuals quadratically. A Student-t likelihood has heavier tails and can reduce the influence of an extreme observation on a location estimate. This changes the model for observations; it does not automatically identify which rows are mistakes.

The synthetic dataset contains eight values between -.3 and .3 plus one value of eight. Two actual PyMC models use the same location and scale priors but different likelihoods. The Student-t model fixes the degrees of freedom at four to keep the example small and its tail assumption explicit.

## Worked case 1: compare posterior locations

The normal model's posterior location is pulled toward the large observation. The Student-t location remains much closer to the central group. The program reports both means and checks that the robust model's location is closer to zero for this deliberately constructed fixture.

This outcome is not a rule that a Student-t model is always preferable. If the large observation is part of the scientific signal, downweighting it can answer the wrong question. If observations arise from distinct subpopulations, a mixture or hierarchical model may be more appropriate. If the record is a data-processing error, correcting the provenance can be better than asking a likelihood to absorb it.

The scale parameter also changes interpretation across likelihood families. A Student-t scale is not its standard deviation in general. For degrees of freedom nu greater than two, the variance is \(\sigma^2\nu/(\nu-2)\). Comparing scale estimates directly with normal standard deviations can therefore mislead.

## Worked case 2: inspect the tail penalty directly

At location zero and scale one, moving an observation from zero to eight changes the normal log density by -32. The Student-t change is much less negative. The code calculates both values independently with SciPy, exposing the mechanism behind the fitted-location difference.

A likelihood's tail behavior affects both inference and prediction. A robust location estimate can coexist with substantial predictive probability for extreme future outcomes. That may be appropriate for heavy-tailed variation, but it should be examined with relevant predictive checks rather than judged only by the location coefficient.

The degrees of freedom control tail thickness. Estimating them introduces another parameter whose posterior can be weakly identified in a small dataset. A fixed value is an assumption, not a conclusion learned from these nine observations. Sensitivity analysis across scientifically plausible tail models is often more useful than reporting a single selected value without context.

## Use posterior predictive criticism

Compare replicated and observed features such as the maximum residual, spread of the central group, asymmetry or subgroup behavior. A normal model might match the overall variance by inflating its scale while failing to represent the dense center. A heavy-tailed model might describe that contrast better but still miss skewness or dependence.

The actual short-chain diagnostics remain part of the output. A robust likelihood can improve some geometry while making other parts of the posterior harder. Do not assume that changing the likelihood solves every computational issue. Effective sample sizes, R-hat, divergences and Monte Carlo errors should be reviewed for the target quantities.

Robust estimation is also distinct from robust decision-making. A decision maker may care precisely about rare extreme costs. A model that reduces outlier influence on a location estimate is not automatically conservative about tail risk. Define the relevant predictive or utility target before selecting the modeling strategy.

## Answered scientific discussion

**Should the extreme row be deleted?** Only with a defensible data-quality or design reason. The example knows how its synthetic data were constructed; an external dataset requires investigation of measurement, units, duplicates and population structure.

**What does the successful program prove?** It demonstrates actual model fitting and a numerical likelihood contrast under explicit priors and a fixed tail parameter. It does not prove which observation model should govern a different dataset or certify the short chains for every tail quantity.

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
```

## Primary references

- [PyMC Student-t distribution](https://www.pymc.io/projects/docs/en/stable/api/distributions/generated/pymc.StudentT.html)
