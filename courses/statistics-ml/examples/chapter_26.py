import numpy as np


def baselines_and_smoothing():
    y = np.array([10.0, 12.0, 14.0, 16.0])
    h = np.arange(1, 4)
    naive = np.repeat(y[-1], 3)
    drift = y[-1] + h * (y[-1] - y[0]) / (len(y) - 1)
    level = y[0]
    for value in y[1:]:
        level = 0.5 * value + 0.5 * level
    assert naive.tolist() == [16.0, 16.0, 16.0]
    assert drift.tolist() == [18.0, 20.0, 22.0] and level == 14.25
    print("Naive:", naive, "drift:", drift, "SES level:", level)


def recursive_ar():
    phi = 0.5
    intercept = 2.0
    current = 10.0
    forecast = []
    for _ in range(4):
        current = intercept + phi * current
        forecast.append(current)
    assert np.allclose(forecast, [7.0, 5.5, 4.75, 4.375])
    assert intercept / (1 - phi) == 4.0
    print("AR forecasts:", forecast, "long-run mean:", 4.0)


def scalar_kalman():
    prior_mean = 0.0
    prior_variance = 4.0
    measurement = 3.0
    measurement_variance = 1.0
    gain = prior_variance / (prior_variance + measurement_variance)
    posterior = prior_mean + gain * (measurement - prior_mean)
    variance = (1 - gain) * prior_variance
    assert np.isclose(gain, 0.8) and np.isclose(posterior, 2.4) and np.isclose(variance, 0.8)
    noisy_gain = 4 / (4 + 16)
    assert noisy_gain < gain
    print("Kalman gain, posterior mean, variance:", gain, posterior, variance)


def volatility_update():
    omega, alpha, beta = 0.1, 0.2, 0.7
    next_variance = omega + alpha * 3**2 + beta * 1.0
    assert np.isclose(next_variance, 2.6) and alpha + beta < 1
    print("Variance after shock 3:", next_variance)


def main():
    baselines_and_smoothing()
    recursive_ar()
    scalar_kalman()
    volatility_update()


if __name__ == "__main__":
    main()
