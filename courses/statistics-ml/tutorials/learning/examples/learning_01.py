"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import stats


def wilson_interval(successes, n, alpha=0.05):
    p = np.asarray(successes) / n
    z = stats.norm.ppf(1 - alpha / 2)
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


def case_01():
    n, successes = 12, 1
    estimate = successes / n
    score = successes / estimate - (n - successes) / (1 - estimate)
    information = n / (estimate * (1 - estimate))
    wald = estimate + np.array([-1, 1]) * stats.norm.ppf(0.975) / np.sqrt(information)
    wilson = wilson_interval(successes, n)
    assert abs(score) < 1e-10 and wald[0] < 0 and wilson[0] > 0
    # Exact enumeration of the sampling distribution, not a Monte Carlo claim.
    s = np.arange(n + 1)
    true_p = 0.05
    probability = stats.binom.pmf(s, n, true_p)
    phat = s / n
    half = stats.norm.ppf(0.975) * np.sqrt(phat * (1 - phat) / n)
    wl, wu = wilson_interval(s, n)
    wald_coverage = probability @ ((phat - half <= true_p) & (true_p <= phat + half))
    wilson_coverage = probability @ ((wl <= true_p) & (true_p <= wu))
    assert wilson_coverage > wald_coverage + 0.3
    result = {
        "mle": estimate,
        "score_at_mle": score,
        "information": information,
        "wald": wald.tolist(),
        "wilson": list(wilson),
        "exact_wald_coverage_at_005": wald_coverage,
        "exact_wilson_coverage_at_005": wilson_coverage,
    }
    print("01 likelihood to coverage:", result)
    return result


def main():
    case_01()


if __name__ == "__main__":
    main()
