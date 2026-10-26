"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
import pandas as pd
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


def case_01():
    users, _, untreated, effect = experiment_fixture()
    observed, se, interval = welch_summary(
        users.loc[users.assigned == 1, "value"], users.loc[users.assigned == 0, "value"]
    )
    assert np.isclose(effect.mean(), 1.6)
    assert np.allclose(users.value, untreated + users.assigned * effect)
    assert np.isclose(effect[users.trigger].mean(), 2)
    result = {
        "finite_population_itt": effect.mean(),
        "trigger_effect": 2.0,
        "observed_contrast": observed,
        "se": se,
        "interval": interval.tolist(),
    }
    print("01 assignment target:", result)
    return result


def main():
    case_01()


if __name__ == "__main__":
    main()
