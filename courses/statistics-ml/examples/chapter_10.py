import numpy as np
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests


def multiple_testing():
    p = np.array([0.001, 0.02, 0.04, 0.3])
    holm = multipletests(p, alpha=0.05, method="holm")[0]
    bh = multipletests(p, alpha=0.05, method="fdr_bh")[0]
    assert holm.tolist() == [True, False, False, False]
    assert bh.tolist() == [True, True, False, False]
    print("Holm decisions:", holm, "BH decisions:", bh)


def spending_and_evidence():
    alpha = 0.05
    t = np.arange(1, 101)
    spending = alpha / (t * (t + 1))
    assert spending.sum() < alpha
    sample = np.random.default_rng(1001).binomial(1, 0.6, size=len(t))
    means = np.cumsum(sample) / t
    radius = np.sqrt(np.log(2 / spending) / (2 * t))
    lower, upper = np.maximum(0, means - radius), np.minimum(1, means + radius)
    assert np.all(lower <= means) and np.all(means <= upper)
    assert radius[-1] < radius[0]
    observations = np.ones(8, dtype=int)
    eprocess = np.cumprod(np.where(observations == 1, 0.8 / 0.5, 0.2 / 0.5))
    assert eprocess[-1] > 20
    null_one_step = 0.5 * (0.8 / 0.5) + 0.5 * (0.2 / 0.5)
    assert null_one_step == 1
    print(
        "Spent alpha:",
        spending.sum(),
        "last Hoeffding radius:",
        radius[-1],
        "likelihood ratio:",
        eprocess[-1],
        "observed final bounded-mean interval:",
        (lower[-1], upper[-1]),
    )


def monitoring_null_paths():
    rng = np.random.default_rng(1010)
    paths, horizon = 4000, 200
    sample = rng.normal(size=(paths, horizon))
    looks = np.arange(20, horizon + 1, 10)
    z = np.cumsum(sample, axis=1)[:, looks - 1] / np.sqrt(looks)
    fixed = np.mean(np.abs(z[:, -1]) > norm.ppf(0.975))
    naive = np.mean(np.any(np.abs(z) > norm.ppf(0.975), axis=1))
    # Bonferroni is conservative but valid for these prespecified looks.
    planned = np.mean(np.any(np.abs(z) > norm.ppf(1 - 0.05 / (2 * len(looks))), axis=1))
    mc_se = np.sqrt(0.05 * 0.95 / paths)
    assert abs(fixed - 0.05) < 4 * mc_se
    assert naive > fixed + 0.03 and planned <= 0.05 + 4 * mc_se
    print(
        "Null false positives fixed/naive/planned:",
        fixed,
        naive,
        planned,
        "Monte Carlo SE at 0.05:",
        mc_se,
    )


def main():
    multiple_testing()
    spending_and_evidence()
    monitoring_null_paths()


if __name__ == "__main__":
    main()
