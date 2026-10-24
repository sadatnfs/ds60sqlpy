import numpy as np
from scipy import stats


def conjugacy_and_prediction():
    prior_a, prior_b = 2.0, 2.0
    successes, trials = 8, 10
    a, b = prior_a + successes, prior_b + trials - successes
    mean = a / (a + b)
    interval = stats.beta.ppf([0.025, 0.975], a, b)
    assert np.isclose(mean, 5 / 7) and interval[0] < mean < interval[1]
    future_variance = mean * (1 - mean)
    parameter_variance = stats.beta.var(a, b)
    assert future_variance > parameter_variance
    print("Posterior mean/interval:", mean, interval, "next binary variance:", future_variance)


def metropolis_reference():
    rng = np.random.default_rng(18)
    current = 0.0
    chain = []
    accepted = 0
    for _ in range(12000):
        proposal = current + rng.normal(scale=1.0)
        log_ratio = -0.5 * proposal**2 + 0.5 * current**2
        if np.log(rng.random()) < min(0.0, log_ratio):
            current = proposal
            accepted += 1
        chain.append(current)
    draws = np.array(chain[2000:])
    assert abs(draws.mean()) < 0.12 and abs(draws.var() - 1) < 0.18
    assert len(set(chain)) < len(chain)
    print("MH normal mean/variance/acceptance:", draws.mean(), draws.var(), accepted / len(chain))


def gaussian_process_conditioning():
    train = np.array([0.0, 1.0])
    test = np.array([0.5, 3.0])
    y = np.array([0.0, 1.0])
    kernel = lambda a, b: np.exp(-0.5 * (a[:, None] - b[None, :]) ** 2)
    k = kernel(train, train) + 0.01 * np.eye(2)
    cross = kernel(test, train)
    mean = cross @ np.linalg.solve(k, y)
    variance = np.diag(kernel(test, test) - cross @ np.linalg.solve(k, cross.T))
    assert np.all(variance >= 0) and variance[1] > variance[0]
    print("GP means:", mean, "latent variances:", variance)


def main():
    conjugacy_and_prediction()
    metropolis_reference()
    gaussian_process_conditioning()


if __name__ == "__main__":
    main()
