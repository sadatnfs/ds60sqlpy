"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np


def case_09():
    # Deliberately separate profile: PyMC 5.28.5 and ArviZ 0.23.4 InferenceData.
    import arviz as az
    import pymc as pm

    rng = np.random.default_rng(1809)
    group = np.repeat(np.arange(6), [3, 5, 8, 10, 12, 15])
    truth = np.array([-1.2, -0.4, 0.0, 0.6, 1.0, 1.5])
    y = truth[group] + rng.normal(scale=1.0, size=len(group))
    with pm.Model(coords={"group": np.arange(6), "observation": np.arange(len(y))}):
        mu = pm.Normal("mu", mu=0, sigma=2)
        tau = pm.HalfNormal("tau", sigma=1)
        z = pm.Normal("z", mu=0, sigma=1, dims="group")
        theta = pm.Deterministic("theta", mu + tau * z, dims="group")
        sigma = pm.HalfNormal("sigma", sigma=2)
        pm.Normal("outcome", mu=theta[group], sigma=sigma, observed=y, dims="observation")
        prior = pm.sample_prior_predictive(samples=200, random_seed=1809)
        fitted = pm.sample(
            draws=600,
            tune=600,
            chains=2,
            cores=1,
            random_seed=1809,
            target_accept=0.95,
            progressbar=False,
            return_inferencedata=True,
        )
        predictive = pm.sample_posterior_predictive(
            fitted, var_names=["outcome"], random_seed=1810, progressbar=False
        )
    assert isinstance(fitted, az.InferenceData)
    summary = az.summary(fitted, var_names=["mu", "tau", "sigma", "theta"], kind="all")
    assert {"r_hat", "ess_bulk", "ess_tail", "mcse_mean"} <= set(summary.columns)
    divergences = int(fitted.sample_stats.diverging.sum())
    posterior_predictive = predictive.posterior_predictive["outcome"].values
    prior_predictive = prior.prior_predictive["outcome"].values
    assert posterior_predictive.shape[-1] == len(y) and np.isfinite(posterior_predictive).all()
    result = {
        "versions": {"pymc": pm.__version__, "arviz": az.__version__},
        "posterior_group_means": fitted.posterior.theta.mean(("chain", "draw")).values.tolist(),
        "observed_group_means": [float(y[group == g].mean()) for g in range(6)],
        "max_rhat": float(summary.r_hat.max()),
        "min_bulk_ess": float(summary.ess_bulk.min()),
        "divergences": divergences,
        "prior_predictive_sd": float(prior_predictive.std()),
        "posterior_predictive_sd": float(posterior_predictive.std()),
        "observed_sd": float(y.std(ddof=1)),
    }
    print("09 PyMC hierarchy and diagnostic evidence:", result)
    print(summary.to_string())
    return result


def main():
    case_09()


if __name__ == "__main__":
    main()
