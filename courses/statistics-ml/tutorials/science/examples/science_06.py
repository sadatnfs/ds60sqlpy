"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import stats


def random_effects(effect, se):
    effect, se = np.asarray(effect), np.asarray(se)
    fixed_weights = 1 / se**2
    fixed = fixed_weights @ effect / fixed_weights.sum()
    q = np.sum(fixed_weights * (effect - fixed) ** 2)
    c = fixed_weights.sum() - np.sum(fixed_weights**2) / fixed_weights.sum()
    tau2 = max(0, (q - (len(effect) - 1)) / c)
    weights = 1 / (se**2 + tau2)
    mean = weights @ effect / weights.sum()
    hk_scale = max(1.0, np.sum(weights * (effect - mean) ** 2) / (len(effect) - 1))
    mean_se = np.sqrt(hk_scale / weights.sum())
    interval = mean + np.array([-1, 1]) * stats.t.ppf(0.975, len(effect) - 1) * mean_se
    prediction = mean + np.array([-1, 1]) * stats.t.ppf(0.975, len(effect) - 2) * np.sqrt(
        tau2 + mean_se**2
    )
    return mean, tau2, interval, prediction


def case_06():
    effect, se = np.array([0.1, 0.3, 0.8, 1.0, -0.2]), np.array([0.1, 0.15, 0.2, 0.18, 0.12])
    mean, tau2, interval, prediction = random_effects(effect, se)
    leave_one_out = [random_effects(np.delete(effect, i), np.delete(se, i))[0] for i in range(5)]
    assert tau2 > 0 and np.ptp(prediction) > np.ptp(interval)
    # A scale transformation must also transform uncertainty.
    converted = random_effects(100 * effect, 100 * se)
    assert np.isclose(converted[0], 100 * mean) and np.isclose(converted[1], 10000 * tau2)
    result = {
        "mean_effect": mean,
        "tau_squared": tau2,
        "modified_hk_ci95": interval.tolist(),
        "approximate_prediction_interval": prediction.tolist(),
        "leave_one_out_means": leave_one_out,
    }
    print("06 synthesis and heterogeneity:", result)
    return result


def main():
    case_06()


if __name__ == "__main__":
    main()
