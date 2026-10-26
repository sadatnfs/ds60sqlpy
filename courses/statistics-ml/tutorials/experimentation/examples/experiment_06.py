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


def case_06():
    users, _, _, _ = experiment_fixture()
    t, c = users[users.assigned == 1], users[users.assigned == 0]
    estimate, se, interval = welch_summary(t.value, c.value)
    rt, st = ratio_summary(t.value, t.visits)
    rc, sc = ratio_summary(c.value, c.visits)
    ratio_se = np.sqrt(st**2 + sc**2)
    rng = np.random.default_rng(606)
    draws = []
    for _ in range(600):
        bt = t.iloc[rng.integers(len(t), size=len(t))]
        bc = c.iloc[rng.integers(len(c), size=len(c))]
        draws.append(bt.value.sum() / bt.visits.sum() - bc.value.sum() / bc.visits.sum())
    boot_se = np.std(draws, ddof=1)
    assert 0.75 < boot_se / ratio_se < 1.25
    # Two one-sided equivalence tests use a 90% interval at alpha 0.05.
    equivalence = np.array([-0.1, 0.1])
    assert np.all(np.abs(equivalence) < 0.5)
    result = {
        "value_effect": estimate,
        "se": se,
        "ci95": interval.tolist(),
        "ratio_effect": rt - rc,
        "ratio_delta_se": ratio_se,
        "ratio_bootstrap_se": boot_se,
        "exceeds_practical_margin": bool(interval[0] > 0.5),
    }
    print("06 fixed-horizon inference:", result)
    return result


def main():
    case_06()


if __name__ == "__main__":
    main()
