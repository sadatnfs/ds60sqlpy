# bayes-010: Centered and noncentered hierarchical computation

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`.

## A hierarchy links related groups without making them identical

A hierarchical model lets group parameters vary while sharing information through a population distribution. In the example, observations have a known noise scale and group means satisfy \(\theta_j\sim\mathcal N(\mu,\tau^2)\). The population mean mu and between-group scale tau are unknown. The amount of pooling depends on both the data and those modeled scales.

Groups have different sample sizes: two, eight and 25. The small first group has an extreme observed mean. The larger third group has an observed mean near one. A sensible explanation should distinguish what each group says directly from what is learned through the shared hierarchy.

## Worked case 1: derive a conditional shrinkage oracle

If mu is zero, tau is one and observation variance is one, the conditional posterior group mean is

\[
\mathbb E[\theta_j\mid\bar y_j,\mu,\tau]
=\frac{n_j\bar y_j}{n_j+1}.
\]

The program calculates this fixed-hyperparameter oracle for all three groups. The first group's mean of -2.5 shrinks to approximately -1.667; the third group's mean of one shrinks to 25/26. The different sample sizes determine how much the group-specific likelihood contributes relative to the same population distribution.

The actual fitted hierarchy estimates mu and tau instead of fixing them. Its posterior means therefore need not equal the oracle. The oracle is a conditional reference calculation that clarifies the mechanism, not an asserted closed-form solution for the full fitted model.

Pooling is an assumption about relatedness. If groups represent fundamentally incompatible mechanisms, a common population distribution can be misleading. Exchangeability is not established simply by giving every group an integer ID. Domain structure, covariates or a different hierarchy may be needed.

## Worked case 2: fit centered and noncentered forms

The centered form samples theta directly from Normal(mu,tau). The noncentered form samples \(z_j\sim\mathcal N(0,1)\) and sets \(\theta_j=\mu+\tau z_j\). Both describe the same intended hierarchy when transformed correctly, but they can have very different posterior geometry.

The program fits both forms using the same bounded configuration and reports their actual diagnostics and posterior group means. It does not assert that one parameterization must have better effective sample size in every case. Weakly informed group effects often motivate noncentering, while strongly informed groups can favor other choices.

A separate density identity checks the parameterization mathematics. For a fixed positive tau and three groups, the centered density evaluated at theta plus \(3\log\tau\) equals the standard-normal density evaluated at z. That Jacobian relationship provides a deterministic check independent of whether either short sampling run appears well mixed.

## Understand the funnel mechanism

When tau is small, all theta values must lie close to mu in the centered representation. When tau is larger, they can spread out. The changing width creates a funnel-like geometry that can be difficult for one numerical step size and metric. Noncentering changes the computational coordinates while preserving the statistical model.

A parameterization is not a free change of scientific meaning. Priors on tau, group-level covariates and observation scales still determine the model. Adding an arbitrary lower bound to tau can remove a difficult region by changing the prior support. That may be justified by knowledge, but it should not be hidden as a convergence repair.

Compare diagnostics for the parameters and derived quantities that matter. A sampler can explore one population parameter adequately while poorly estimating an extreme group effect or a new-group prediction. The two short chains here are a demonstration of these observations, not sufficient evidence for every hierarchical decision.

## Answered scientific discussion

**Does shrinkage imply that the raw group estimate was wrong?** It represents a model-based combination of group evidence and population information. Its usefulness depends on the model and the decision. Report both the observed group data and the assumptions supporting partial pooling.

**Should centered and noncentered sampled means be exactly equal?** No. They are Monte Carlo approximations, possibly with different computational errors. Large differences should motivate investigation, but closeness alone cannot prove that both runs explored the complete posterior.

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
```

## Primary references

- [Betancourt, hierarchical model geometry](https://arxiv.org/abs/1312.0906)
