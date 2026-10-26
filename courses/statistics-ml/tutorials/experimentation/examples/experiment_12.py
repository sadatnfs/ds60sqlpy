"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
import pandas as pd


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


def launch_decision(effect_interval, guardrail_upper, integrity_ok, mature, margin=0.5):
    if not integrity_ok or not mature:
        return "investigate or wait"
    if guardrail_upper >= 0.1:
        return "guardrail unresolved"
    if effect_interval[0] > margin:
        return "eligible for bounded rollout"
    return "inconclusive against practical margin"


def case_12():
    users, _, _, _ = experiment_fixture()
    mature = users.age_days >= 7
    assert mature.sum() < len(users)
    # Equal randomized cohorts are followed to the same exposure age.
    ages = np.array([1, 7, 14, 28])
    effect = 0.2 + 1.8 * np.exp(-(ages - 1) / 7)
    assert effect[0] == 2 and effect[-1] < 0.3
    decisions = [
        launch_decision([0.7, 1.3], 0.08, True, True),
        launch_decision([0.7, 1.3], 0.08, False, True),
        launch_decision([-0.2, 1.3], 0.08, True, True),
        launch_decision([0.7, 1.3], 0.15, True, True),
    ]
    assert len(set(decisions)) == 4
    result = {
        "mature_users": int(mature.sum()),
        "all_users": len(users),
        "age_specific_effects": list(zip(ages.tolist(), effect.tolist(), strict=True)),
        "decision_cases": decisions,
    }
    print("12 decision memo inputs:", result)
    return result


def main():
    case_12()


if __name__ == "__main__":
    main()
