"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import special


def case_08():
    rng = np.random.default_rng(1908)
    n, delta = 1000, 0.05
    thresholds = np.linspace(0, 1, 41)  # Fixed before the sample.
    x = rng.uniform(size=n)
    y = rng.binomial(1, 0.2 + 0.6 * x)
    empirical = ((x[:, None] >= thresholds) != y[:, None]).mean(axis=0)
    risk = 0.5 - 0.6 * thresholds + 0.6 * thresholds**2
    radius = np.sqrt(np.log(2 * len(thresholds) / delta) / (2 * n))
    chosen = np.argmin(empirical)
    assert np.all(np.abs(empirical - risk) < radius)
    assert risk[chosen] - risk.min() <= 2 * radius
    # A fixed uniform prior and a data-dependent Gibbs posterior over finite rules.
    posterior = special.softmax(-20 * empirical)
    kl = np.sum(special.xlogy(posterior, posterior * len(thresholds)))
    rhs = (kl + np.log(2 * np.sqrt(n) / delta)) / n
    gibbs_empirical, gibbs_risk = posterior @ empirical, posterior @ risk
    upper = min(1.0, gibbs_empirical + np.sqrt(rhs / 2))
    assert kl >= 0 and gibbs_risk <= upper
    result = {
        "hypotheses": len(thresholds),
        "uniform_radius": radius,
        "selected_threshold": thresholds[chosen],
        "empirical_risk": empirical[chosen],
        "true_risk": risk[chosen],
        "oracle_risk": risk.min(),
        "gibbs_kl": kl,
        "gibbs_true_risk": gibbs_risk,
        "pac_bayes_upper": upper,
    }
    print("08 learning guarantees and assumptions:", result)
    return result


def main():
    case_08()


if __name__ == "__main__":
    main()
