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


def case_05():
    users, _, _, _ = experiment_fixture()
    counts = users.groupby("assigned").size().to_numpy()
    # Complete randomization fixes these counts. The diagnostic model below is
    # multinomial allocation, appropriate for independent hash allocation in deployment.
    valid_srm = stats.chisquare(counts).pvalue
    broken = users.loc[~((users.assigned == 1) & (users.device == "mobile"))]
    broken_srm = stats.chisquare(broken.groupby("assigned").size()).pvalue
    stage = broken.groupby(["device", "assigned"]).size().unstack(fill_value=0)
    rng = np.random.default_rng(505)
    aa = rng.binomial(1000, 0.5, size=4000)
    aa_p = stats.chisquare(np.column_stack([aa, 1000 - aa]), axis=1).pvalue
    rate = np.mean(aa_p < 0.01)
    mc_se = np.sqrt(0.01 * 0.99 / len(aa))
    assert valid_srm == 1 and broken_srm < 0.01
    assert stage.loc["mobile", 1] == 0
    assert abs(rate - 0.01) < 4 * mc_se
    result = {
        "assignment_srm_p": valid_srm,
        "broken_stage_srm_p": broken_srm,
        "mobile_counts": stage.loc["mobile"].to_dict(),
        "aa_false_alarm_rate": rate,
        "aa_mc_se": mc_se,
    }
    print("05 integrity localization:", result)
    return result


def main():
    case_05()


if __name__ == "__main__":
    main()
