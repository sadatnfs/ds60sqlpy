"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


def experiment_fixture():
    """One user per assignment; several events per user; treatment is randomized."""
    rng = np.random.default_rng(20261025)
    n = 240
    unit = np.arange(n)
    assigned = rng.permutation(np.repeat([0, 1], n // 2))
    baseline = rng.uniform(-2, 2, n)
    trigger = unit % 5 != 0  # Fixed before assignment; valid for both arms.
    visits = rng.poisson(3, n) + 1
    untreated = 20 + 4 * baseline + rng.normal(size=n)
    effect = 2.0 * trigger
    value = untreated + assigned * effect
    converted = rng.binomial(1, 0.20 + 0.04 * assigned * trigger)
    users = pd.DataFrame(
        {
            "unit": unit,
            "assigned": assigned,
            "baseline": baseline,
            "trigger": trigger,
            "visits": visits,
            "value": value,
            "converted": converted,
            "device": np.where(unit % 3 == 0, "mobile", "desktop"),
            "age_days": unit % 35 + 1,
        }
    )
    events = pd.DataFrame(
        {
            "unit": np.repeat(unit, visits),
            "points": np.repeat(value / visits, visits),
        }
    )
    events["event_id"] = np.arange(len(events))
    assert users.unit.is_unique and events.event_id.is_unique
    assert np.isclose(events.points.sum(), users.value.sum())
    return users, events, untreated, effect


def welch_summary(treated, control, alpha=0.05):
    treated, control = np.asarray(treated), np.asarray(control)
    vt, vc = treated.var(ddof=1) / len(treated), control.var(ddof=1) / len(control)
    se = np.sqrt(vt + vc)
    df = (vt + vc) ** 2 / (vt**2 / (len(treated) - 1) + vc**2 / (len(control) - 1))
    effect = treated.mean() - control.mean()
    interval = effect + np.array([-1, 1]) * stats.t.ppf(1 - alpha / 2, df) * se
    return effect, se, interval


def case_07():
    users, _, _, effect = experiment_fixture()
    a = users.assigned.to_numpy()
    x = users.baseline.to_numpy() - users.baseline.mean()
    design = np.column_stack([np.ones(len(a)), a, x, a * x])
    adjusted = sm.OLS(users.value, design).fit(cov_type="HC2")
    raw, raw_se, _ = welch_summary(users.loc[a == 1, "value"], users.loc[a == 0, "value"])
    estimate, se = adjusted.params.iloc[1], adjusted.bse.iloc[1]
    assert se < raw_se and abs(estimate - effect.mean()) < 0.5
    # Known linear coefficient illustrates why adjustment changes a realized contrast.
    residualized = users.value - 4 * x
    adjusted_known = residualized[a == 1].mean() - residualized[a == 0].mean()
    imbalance = x[a == 1].mean() - x[a == 0].mean()
    assert np.isclose(adjusted_known, raw - 4 * imbalance)
    result = {
        "raw_effect": raw,
        "adjusted_effect": estimate,
        "raw_se": raw_se,
        "adjusted_hc2_se": se,
        "true_fixture_itt": effect.mean(),
        "baseline_imbalance": imbalance,
        "ci95": (estimate + np.array([-1, 1]) * stats.norm.ppf(0.975) * se).tolist(),
    }
    print("07 adjustment and uncertainty:", result)
    return result


def main():
    case_07()


if __name__ == "__main__":
    main()
