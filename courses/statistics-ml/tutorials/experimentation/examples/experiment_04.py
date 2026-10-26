"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import stats


def normal_total_size(sd_control, sd_treatment, delta, fraction=0.5, power=0.8, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return z**2 * (sd_treatment**2 / fraction + sd_control**2 / (1 - fraction)) / delta**2


def case_04():
    total = normal_total_size(2, 2, 1)
    smaller = normal_total_size(2, 2, 0.5)
    unequal = normal_total_size(2, 2, 1, fraction=0.8)
    binary = normal_total_size(np.sqrt(0.20 * 0.80), np.sqrt(0.24 * 0.76), 0.04)
    eligible_daily = 300 * 0.8
    enrollment_days = int(np.ceil(binary / eligible_daily))
    mature_days = enrollment_days + 7
    deff = 1 + (12 - 1) * 0.1
    assert np.isclose(smaller, 4 * total) and unequal > total
    assert np.isclose(deff, 2.1)
    sizes = np.array([50, 100, 200, 400])
    noncentral = 1 / (2 * np.sqrt(2 / sizes))
    power = stats.norm.sf(stats.norm.ppf(0.975) - noncentral)
    power += stats.norm.cdf(-stats.norm.ppf(0.975) - noncentral)
    assert np.all(np.diff(power) > 0)
    result = {
        "continuous_total": int(np.ceil(total)),
        "unequal_total": int(np.ceil(unequal)),
        "binary_total_approx": int(np.ceil(binary)),
        "calendar_days": mature_days,
        "cluster_design_effect": deff,
        "per_arm_power_curve": list(zip(sizes.tolist(), power.tolist(), strict=True)),
    }
    print("04 information budget:", result)
    return result


def main():
    case_04()


if __name__ == "__main__":
    main()
