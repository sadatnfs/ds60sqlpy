import numpy as np


def bayes_and_total_variance():
    prevalence, sensitivity, false_positive = 0.01, 0.9, 0.05
    positive = prevalence * sensitivity + (1 - prevalence) * false_positive
    posterior = prevalence * sensitivity / positive
    assert 0.15 < posterior < 0.16
    weights, means, variances = np.array([0.25, 0.75]), np.array([0.0, 4.0]), np.array([1.0, 1.0])
    mean = weights @ means
    variance = weights @ variances + weights @ (means - mean) ** 2
    assert mean == 3 and variance == 4
    print("P(event | alert):", round(posterior, 4), "mixture variance:", variance)


def markov_and_jensen():
    transition = np.array([[0.8, 0.2], [0.4, 0.6]])
    stationary = np.array([2 / 3, 1 / 3])
    assert np.allclose(stationary @ transition, stationary)
    distribution = np.array([1.0, 0.0]) @ np.linalg.matrix_power(transition, 20)
    assert np.allclose(distribution, stationary, atol=1e-7)
    x = np.array([1.0, 3.0])
    assert np.mean(x * x) > np.mean(x) ** 2
    print(
        "Long-run state probabilities:",
        distribution,
        "variance gap:",
        np.mean(x * x) - np.mean(x) ** 2,
    )


def central_limit_simulation():
    rng = np.random.default_rng(303)
    samples = rng.exponential(size=(6000, 32))
    standardized = np.sqrt(32) * (samples.mean(axis=1) - 1)
    assert abs(standardized.mean()) < 0.06
    assert abs(standardized.var(ddof=1) - 1) < 0.08
    raw_skew = np.mean((samples[:, 0] - samples[:, 0].mean()) ** 3) / samples[:, 0].std() ** 3
    mean_skew = np.mean((standardized - standardized.mean()) ** 3) / standardized.std() ** 3
    assert abs(mean_skew) < abs(raw_skew)
    print(
        "CLT standardized mean/variance:",
        standardized.mean(),
        standardized.var(ddof=1),
        "raw/mean skew:",
        raw_skew,
        mean_skew,
    )


def main():
    central_limit_simulation()
    bayes_and_total_variance()
    markov_and_jensen()


if __name__ == "__main__":
    main()
