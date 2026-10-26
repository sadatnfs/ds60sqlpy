import numpy as np
import statsmodels.api as sm
from scipy import stats


def allocation_integrity():
    result = stats.chisquare([600, 400], f_exp=[500, 500])
    assert result.pvalue < 1e-8
    print("SRM statistic/p:", result.statistic, result.pvalue)


def cuped():
    x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    noise = np.array([1.0, -2.0, 2.0, -2.0, 1.0])
    y = 10 + 3 * x + noise
    theta = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    adjusted = y - theta * (x - x.mean())
    assert np.isclose(theta, 3) and np.isclose(adjusted.mean(), y.mean())
    rho = np.corrcoef(x, y)[0, 1]
    assert np.isclose(adjusted.var(ddof=1), y.var(ddof=1) * (1 - rho**2))
    print("CUPED theta:", theta, "variance before/after:", y.var(ddof=1), adjusted.var(ddof=1))


def ratio_metric():
    revenue = np.array([1.0, 9.0, 4.0, 8.0])
    visits = np.array([1.0, 3.0, 2.0, 4.0])
    ratio = revenue.sum() / visits.sum()
    influence = (revenue - ratio * visits) / visits.mean()
    se = influence.std(ddof=1) / np.sqrt(len(visits))
    assert np.isclose(ratio, 2.2) and np.isclose(np.mean(revenue / visits), 2.0)
    assert abs(influence.mean()) < 1e-12 and se > 0
    print("Ratio of totals:", ratio, "mean user ratio:", np.mean(revenue / visits), "delta SE:", se)


def adjusted_randomized_comparison():
    rng = np.random.default_rng(1407)
    n = 240
    baseline = rng.normal(size=n)
    assigned = rng.permutation(np.repeat([0.0, 1.0], n // 2))
    outcome = 10 + 2 * assigned + 3 * baseline + rng.normal(size=n)
    centered = baseline - baseline.mean()
    design = np.column_stack([np.ones(n), assigned, centered, assigned * centered])
    fit = sm.OLS(outcome, design).fit(cov_type="HC2")
    treated, control = outcome[assigned == 1], outcome[assigned == 0]
    raw = treated.mean() - control.mean()
    raw_se = np.sqrt(treated.var(ddof=1) / len(treated) + control.var(ddof=1) / len(control))
    adjusted, se = fit.params[1], fit.bse[1]
    interval = adjusted + np.array([-1, 1]) * stats.norm.ppf(0.975) * se
    assert se < raw_se and abs(adjusted - 2) < 0.5
    assert np.linalg.matrix_rank(design) == 4
    print(
        "Assignment effect raw/adjusted:",
        raw,
        adjusted,
        "SE raw/HC2:",
        raw_se,
        se,
        "adjusted approximate 95% CI:",
        interval,
    )
    # This fixture illustrates precision; one interval cannot establish coverage.


def main():
    allocation_integrity()
    cuped()
    ratio_metric()
    adjusted_randomized_comparison()


if __name__ == "__main__":
    main()
