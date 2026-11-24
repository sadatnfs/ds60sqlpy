# bayes-010: Centered and noncentered hierarchical computation

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-009`.

## A hierarchy links related groups without making them identical

A hierarchical model lets group parameters vary while sharing information through a population distribution. In the example, observations have a known noise scale and group means satisfy \(\theta_j\sim\mathcal N(\mu,\tau^2)\). The population mean mu and between-group scale tau are unknown. The amount of pooling depends on both the data and those modeled scales.

Groups have different sample sizes: two, eight and 25. The small first group has an extreme observed mean. The larger third group has an observed mean near one. A sensible explanation should distinguish what each group says directly from what is learned through the shared hierarchy.

## Key terms

- **Hierarchical model:** A model in which group parameters vary around a population distribution, here theta_j ~ Normal(mu, tau^2).
- **Partial pooling:** Shrinking each group estimate toward the population mean by an amount set by its data and the modeled scale tau.
- **Noncentered parameterization:** Writing theta_j = mu + tau z_j with standard-normal z_j instead of sampling theta_j directly.
- **Funnel geometry:** A posterior whose width in theta shrinks sharply as tau approaches zero, which defeats one fixed step size.

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

Compare diagnostics for the parameters and derived quantities that matter. A sampler can explore one population parameter adequately while poorly estimating an extreme group effect or a new-group prediction. The two short chains here are a demonstration of these observations, not sufficient evidence for every hierarchical decision. Apply the same screen to each parameterization's record (R-hat below 1.01, at least 100 bulk effective draws per chain and zero divergences); with 120 retained draws per chain, either form may fail it, and a divergence in the centered fit is a geometry signal rather than noise.

## Answered scientific discussion

**Does shrinkage imply that the raw group estimate was wrong?** It represents a model-based combination of group evidence and population information. Its usefulness depends on the model and the decision. Report both the observed group data and the assumptions supporting partial pooling.

**Should centered and noncentered sampled means be exactly equal?** No. They are Monte Carlo approximations, possibly with different computational errors. Large differences should motivate investigation, but closeness alone cannot prove that both runs explored the complete posterior.

## Worked example: Marginal posterior of tau on a grid for eight groups

```python
import numpy as np

y = np.array([28.0, 8.0, -3.0, 7.0, -1.0, 1.0, 18.0, 12.0])
s = np.array([15.0, 10.0, 16.0, 11.0, 9.0, 11.0, 10.0, 18.0])
tau = np.linspace(0.01, 40, 4000)


def log_marg(t):  # mu integrated out under a flat prior
    v = s**2 + t**2
    V = 1 / np.sum(1 / v)
    mu = V * np.sum(y / v)
    return 0.5 * np.log(V) - 0.5 * np.sum(np.log(v)) - 0.5 * np.sum((y - mu) ** 2 / v)


lp = np.array([log_marg(t) for t in tau]) + np.log(1 / (1 + (tau / 5) ** 2))  # half-Cauchy(0, 5)
w = np.exp(lp - lp.max())
w /= w.sum()
cdf = np.cumsum(w)
print(
    f"P(tau < 2 | y) = {cdf[tau < 2][-1]:.3f}; posterior median tau {tau[np.searchsorted(cdf, 0.5)]:.2f}"
)
for t in (0.5, 2.0, 10.0):
    print(f"tau {t:>4}: pooling weight on group 1's own estimate {t**2 / (t**2 + s[0] ** 2):.4f}")
```

Observed output:

```text
P(tau < 2 | y) = 0.378; posterior median tau 2.78
tau  0.5: pooling weight on group 1's own estimate 0.0011
tau  2.0: pooling weight on group 1's own estimate 0.0175
tau 10.0: pooling weight on group 1's own estimate 0.3077
```

Integrating the group mean out analytically leaves a one-dimensional posterior for the between-group scale \(\tau\), which a fine grid can evaluate exactly. Under a half-Cauchy(0, 5) prior these eight groups put 0.378 of the posterior mass below \(\tau=2\), and the median is only 2.78. The data are consistent with very little between-group variation. That matters for computation because of the pooling weights. Group 1's estimate has standard error 15, so its own data receive weight \(\tau^2/(\tau^2+225)\): 0.0011 at \(\tau=0.5\), 0.0175 at 2 and 0.3077 at 10. In the region the posterior visits often, each group effect is pinned tightly to the common mean, with conditional standard deviation close to \(\tau\) itself. A centered sampler must move \(\tau\) and every group effect together through that narrow neck, which is the funnel. The noncentered form samples standardized deviations whose scale does not change with \(\tau\), so the same posterior becomes much easier to explore.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `bayesian-cpu`.

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

    rhat = np.asarray(az.rhat(trace, var_names=names).to_dataarray(), float)
    ess = np.asarray(az.ess(trace, var_names=names, method="bulk").to_dataarray(), float)

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
