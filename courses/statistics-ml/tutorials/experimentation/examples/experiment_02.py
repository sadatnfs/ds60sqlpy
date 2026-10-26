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


def ratio_summary(numerator, denominator):
    numerator, denominator = np.asarray(numerator), np.asarray(denominator)
    if numerator.shape != denominator.shape or numerator.ndim != 1 or len(numerator) < 2:
        raise ValueError(
            "Ratio uncertainty requires matching vectors with at least two independent units"
        )
    if (
        not np.isfinite(numerator).all()
        or not np.isfinite(denominator).all()
        or denominator.sum() <= 0
    ):
        raise ValueError("Ratio contributions must be finite with a positive total denominator")
    ratio = numerator.sum() / denominator.sum()
    influence = (numerator - ratio * denominator) / denominator.mean()
    return ratio, influence.std(ddof=1) / np.sqrt(len(influence))


def case_02():
    users, events, _, _ = experiment_fixture()
    user_mean = users.value.mean()
    ratio, se = ratio_summary(users.value, users.visits)
    mean_ratios = (users.value / users.visits).mean()
    event_mean = events.points.mean()
    assert np.isclose(event_mean, ratio) and not np.isclose(ratio, mean_ratios)
    result = {
        "points_per_assigned_user": user_mean,
        "points_per_visit": ratio,
        "mean_user_ratios": mean_ratios,
        "ratio_user_se": se,
    }
    print("02 metric denominators:", result)
    return result


def main():
    case_02()


if __name__ == "__main__":
    main()
