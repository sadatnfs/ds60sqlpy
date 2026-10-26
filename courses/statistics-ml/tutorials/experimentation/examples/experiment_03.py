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


def case_03():
    users, events, _, _ = experiment_fixture()
    duplicate = pd.concat([events, events.iloc[:10]], ignore_index=True)
    wrong_total = duplicate.points.sum()
    clean = duplicate.drop_duplicates("event_id")
    aggregate = clean.groupby("unit", as_index=False).points.sum()
    joined = users.merge(aggregate, on="unit", how="left", validate="one_to_one")
    assert np.allclose(joined.points, joined.value)
    failed = (users.assigned == 1) & (users.device == "mobile") & (users.converted == 0)
    observed_only = users.loc[~failed]
    conversion = users.groupby("assigned").converted.mean()
    biased = observed_only.groupby("assigned").converted.mean()
    assert biased.loc[1] > conversion.loc[1]
    result = {
        "duplicate_excess": wrong_total - clean.points.sum(),
        "lost_exposures": int(failed.sum()),
        "assignment_conversion": conversion.to_dict(),
        "logged_only_conversion": biased.to_dict(),
    }
    print("03 instrumentation defect:", result)
    return result


def main():
    case_03()


if __name__ == "__main__":
    main()
