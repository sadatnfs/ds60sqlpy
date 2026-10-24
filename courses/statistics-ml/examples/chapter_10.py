import numpy as np
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
    means = np.full(100, 0.6)
    radius = np.sqrt(np.log(2 / spending) / (2 * t))
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
    )


def main():
    multiple_testing()
    spending_and_evidence()


if __name__ == "__main__":
    main()
