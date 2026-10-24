import numpy as np
from scipy import stats


def robust_location():
    clean = np.array([9.0, 10.0, 10.0, 11.0, 10.0])
    contaminated = np.append(clean, 1000.0)
    median = np.median(contaminated)
    trimmed = stats.trim_mean(contaminated, proportiontocut=1 / 6)
    assert median == 10 and trimmed == 10.25
    assert contaminated.mean() > 100
    residual = np.array([0.0, 1.0, 100.0])
    huber_score = np.clip(residual, -1.5, 1.5)
    assert huber_score[-1] == 1.5
    print(
        "Mean/median/trimmed:", contaminated.mean(), median, trimmed, "Huber scores:", huber_score
    )


def imputation_uncertainty():
    estimates = np.array([2.0, 2.5, 3.0])
    within_variance = np.array([0.04, 0.04, 0.04])
    m = len(estimates)
    between = estimates.var(ddof=1)
    total = within_variance.mean() + (1 + 1 / m) * between
    assert np.isclose(total, 0.04 + 1 / 3) and total > within_variance.mean()
    observed_mean, missing_fraction = 2.0, 0.3
    deltas = np.array([-2.0, 0.0, 2.0])
    sensitivity = observed_mean + missing_fraction * deltas
    assert np.allclose(sensitivity, [1.4, 2.0, 2.6])
    print("Pooled estimate/SE:", estimates.mean(), np.sqrt(total), "MNAR scenarios:", sensitivity)


def measurement_error_attenuation():
    x = np.array([-1.0, -1.0, 1.0, 1.0])
    error = np.array([-1.0, 1.0, -1.0, 1.0])
    observed = x + error
    y = 2 * x
    slope = np.sum((observed - observed.mean()) * (y - y.mean())) / np.sum(
        (observed - observed.mean()) ** 2
    )
    reliability = np.var(x) / (np.var(x) + np.var(error))
    assert np.isclose(slope, 1.0) and np.isclose(slope, 2 * reliability)
    print("True slope 2; noisy-predictor slope:", slope, "reliability ratio:", reliability)


def main():
    measurement_error_attenuation()
    robust_location()
    imputation_uncertainty()


if __name__ == "__main__":
    main()
