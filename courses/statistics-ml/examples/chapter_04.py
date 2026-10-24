import numpy as np
from scipy import stats


def counts_and_tails():
    n, p = 10, 0.2
    assert np.isclose(stats.binom.mean(n, p), 2)
    poisson_var = stats.poisson.var(2)
    beta_binomial_var = stats.betabinom.var(n, 2, 8)
    assert beta_binomial_var > stats.binom.var(n, p)
    print("Binomial variance:", stats.binom.var(n, p), "beta-binomial variance:", beta_binomial_var)
    assert poisson_var == 2
    assert stats.t.sf(3, df=3) > stats.norm.sf(3)


def positive_and_truncated():
    mu, sigma = 0.0, 1.0
    arithmetic = stats.lognorm.mean(s=sigma, scale=np.exp(mu))
    median = stats.lognorm.median(s=sigma, scale=np.exp(mu))
    assert arithmetic > median == 1
    conditional = (stats.norm.cdf(1) - stats.norm.cdf(0)) / (1 - stats.norm.cdf(0))
    assert np.isclose(conditional, stats.truncnorm.cdf(1, 0, np.inf))
    assert np.isclose(
        stats.expon.sf(5, scale=2) / stats.expon.sf(3, scale=2), stats.expon.sf(2, scale=2)
    )
    print(
        "Lognormal mean/median:",
        round(arithmetic, 4),
        median,
        "P(Z<=1 | Z>0):",
        round(conditional, 4),
    )


def mixtures_and_zeros():
    weight = np.array([0.8, 0.2])
    means = np.array([1.0, 6.0])
    variances = np.array([1.0, 1.0])
    mean = weight @ means
    variance = weight @ variances + weight @ (means - mean) ** 2
    assert np.isclose(mean, 2) and np.isclose(variance, 5)
    structural_zero = 0.3
    rate = 2.0
    zero_probability = structural_zero + (1 - structural_zero) * stats.poisson.pmf(0, rate)
    assert zero_probability > stats.poisson.pmf(0, rate)
    assert np.isclose((1 - structural_zero) * rate, 1.4)
    print("Mixture mean/variance:", mean, variance, "zero-inflated P(0):", zero_probability)


def main():
    mixtures_and_zeros()
    counts_and_tails()
    positive_and_truncated()


if __name__ == "__main__":
    main()
