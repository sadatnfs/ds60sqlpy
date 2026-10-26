"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np


def case_02():
    # Known group/noise variances isolate posterior calculation from MCMC.
    means = np.array([-1.0, 0.2, 1.4])
    sizes = np.array([2, 10, 30])
    prior_mean, tau2, sigma2 = 0.0, 1.0, 4.0
    posterior_variance = 1 / (1 / tau2 + sizes / sigma2)
    weight = sizes * tau2 / (sigma2 + sizes * tau2)
    posterior_mean = weight * means + (1 - weight) * prior_mean
    predictive_sd = np.sqrt(posterior_variance + sigma2)
    assert np.all(np.diff(weight) > 0) and np.all(predictive_sd > np.sqrt(posterior_variance))
    rng = np.random.default_rng(1802)
    draws = rng.normal(posterior_mean, np.sqrt(posterior_variance), size=(6000, 3))
    predictive = draws + rng.normal(0, np.sqrt(sigma2), size=draws.shape)
    assert np.allclose(predictive.var(axis=0), predictive_sd**2, rtol=0.07)
    narrow_prior = (sizes / sigma2 * means) / (1 / 0.25 + sizes / sigma2)
    # Posterior expected shortage cost at a candidate action, not just parameter means.
    action = 2.0
    loss = 4 * np.maximum(predictive - action, 0) + np.maximum(action - predictive, 0)
    result = {
        "unpooled_means": means.tolist(),
        "pooling_weights": weight.tolist(),
        "posterior_means": posterior_mean.tolist(),
        "posterior_sd": np.sqrt(posterior_variance).tolist(),
        "predictive_sd": predictive_sd.tolist(),
        "narrow_prior_means": narrow_prior.tolist(),
        "expected_asymmetric_loss_at_2": loss.mean(axis=0).tolist(),
    }
    print("02 posterior, prediction and decision:", result)
    return result


def main():
    case_02()


if __name__ == "__main__":
    main()
