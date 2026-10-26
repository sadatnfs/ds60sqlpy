"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import special


def case_08():
    rng = np.random.default_rng(1708)
    n = 30000
    l0 = rng.binomial(1, 0.5, n)
    e0 = special.expit(-0.4 + 0.8 * l0)
    a0 = rng.binomial(1, e0)
    l1 = rng.binomial(1, special.expit(l0 - a0))
    e1 = special.expit(-0.4 + l1)
    a1 = rng.binomial(1, e1)
    y = 1 + 2 * a0 + 3 * a1 + l0 + l1 + rng.normal(size=n)
    regime_means = []
    oracle = []
    for regime in (0, 1):
        probability = np.where(regime == 1, e0, 1 - e0) * np.where(regime == 1, e1, 1 - e1)
        assert np.all((probability > 0) & (probability < 1))
        consistent = (a0 == regime) & (a1 == regime)
        regime_means.append(np.mean(consistent * y / probability))
        oracle.append(1 + 5 * regime + 0.5 + np.mean(special.expit(np.array([0, 1]) - regime)))
    effect, true_effect = np.diff(regime_means)[0], np.diff(oracle)[0]
    assert abs(effect - true_effect) < 0.2 and true_effect < 5
    result = {
        "sustained_regime_ipw_means": regime_means,
        "oracle_regime_means": oracle,
        "ipw_total_effect": effect,
        "oracle_total_effect": true_effect,
        "controlled_direct_coefficient_sum": 5.0,
    }
    print("08 treatment-confounder feedback:", result)
    return result


def main():
    case_08()


if __name__ == "__main__":
    main()
