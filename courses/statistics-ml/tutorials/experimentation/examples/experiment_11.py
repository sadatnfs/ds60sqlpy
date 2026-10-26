"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import stats


def welch_summary(treated, control, alpha=0.05):
    treated, control = np.asarray(treated), np.asarray(control)
    vt, vc = treated.var(ddof=1) / len(treated), control.var(ddof=1) / len(control)
    se = np.sqrt(vt + vc)
    df = (vt + vc) ** 2 / (vt**2 / (len(treated) - 1) + vc**2 / (len(control) - 1))
    effect = treated.mean() - control.mean()
    interval = effect + np.array([-1, 1]) * stats.t.ppf(1 - alpha / 2, df) * se
    return effect, se, interval


def case_11():
    rng = np.random.default_rng(1111)
    pairs = 30
    order = rng.binomial(1, 0.5, pairs)
    treatment = np.column_stack([order, 1 - order]).ravel()
    baseline = np.repeat(np.linspace(10, 12, pairs), 2)
    outcome = baseline + 1.5 * treatment + rng.normal(size=2 * pairs)
    contrasts = np.array(
        [
            outcome[2 * i : 2 * i + 2][treatment[2 * i : 2 * i + 2] == 1][0]
            - outcome[2 * i : 2 * i + 2][treatment[2 * i : 2 * i + 2] == 0][0]
            for i in range(pairs)
        ]
    )
    estimate = contrasts.mean()
    assert np.isclose(estimate, outcome[treatment == 1].mean() - outcome[treatment == 0].mean())
    se = contrasts.std(ddof=1) / np.sqrt(pairs)
    interval = estimate + np.array([-1, 1]) * stats.t.ppf(0.975, pairs - 1) * se
    # Forty sessions repeat each block shock; they are not forty independent assignments.
    repeated_y, repeated_a = np.repeat(outcome, 40), np.repeat(treatment, 40)
    _, wrong_se, _ = welch_summary(repeated_y[repeated_a == 1], repeated_y[repeated_a == 0])
    assert wrong_se < se / 2
    carryover = outcome + 0.8 * np.r_[0, treatment[:-1]]
    contaminated = carryover[treatment == 1].mean() - carryover[treatment == 0].mean()
    result = {
        "paired_effect": estimate,
        "paired_se": se,
        "ci95": interval.tolist(),
        "incorrect_session_se": wrong_se,
        "contrast_with_carryover": contaminated,
    }
    print("11 switchback information:", result)
    return result


def main():
    case_11()


if __name__ == "__main__":
    main()
