"""Durable source for twelve standalone, offline experiment demonstrations.

build_examples.py selects a case and its helper closure for the classroom pad.
No data acquisition, file writes or external services are part of these cases.
"""

from itertools import product

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests


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


def case_08():
    rng = np.random.default_rng(808)
    looks = np.arange(20, 201, 10)
    observations = rng.normal(size=(4000, 200))
    z = observations.cumsum(axis=1)[:, looks - 1] / np.sqrt(looks)
    naive = np.mean(np.any(np.abs(z) > stats.norm.ppf(0.975), axis=1))
    fixed = np.mean(np.abs(z[:, -1]) > stats.norm.ppf(0.975))
    planned = np.mean(np.any(np.abs(z) > stats.norm.ppf(1 - 0.05 / (2 * len(looks))), axis=1))
    mc_se = np.sqrt(0.05 * 0.95 / len(z))
    assert naive > fixed + 0.03 and planned < 0.05 + 4 * mc_se
    path = rng.binomial(1, 0.6, 200)
    n = np.arange(1, len(path) + 1)
    allocated_alpha = 0.05 / (n * (n + 1))
    radius = np.sqrt(np.log(2 / allocated_alpha) / (2 * n))
    mean = path.cumsum() / n
    lower, upper = np.maximum(0, mean - radius), np.minimum(1, mean + radius)
    evidence = np.cumprod(np.where(path == 1, 0.6 / 0.5, 0.4 / 0.5))
    holm = multipletests([0.001, 0.02, 0.04, 0.3], method="holm")[0]
    assert allocated_alpha.sum() < 0.05 and holm.sum() == 1
    result = {
        "null_fixed": fixed,
        "null_peeking": naive,
        "null_planned": planned,
        "mc_se_at_alpha": mc_se,
        "observed_cs_final": [lower[-1], upper[-1]],
        "evidence_crossed_20": bool(np.any(evidence >= 20)),
        "holm": holm.tolist(),
    }
    print("08 monitoring procedures:", result)
    return result


def case_09():
    # Two replications per factorial cell give residual degrees of freedom.
    cells = np.array(list(product([-1.0, 1.0], repeat=2)))
    factors = np.repeat(cells, 2, axis=0)
    a, b = factors.T
    noise = np.tile([-0.5, 0.5], 4)
    design = np.column_stack([np.ones(8), a, b, a * b])
    y = 10 + 2 * a + 3 * b + 4 * a * b + noise
    fit = sm.OLS(y, design).fit()
    assert np.allclose(fit.params, [10, 2, 3, 4]) and fit.df_resid == 4
    effects = {
        "A_average": 2 * fit.params[1],
        "A_at_B_low": 2 * (fit.params[1] - fit.params[3]),
        "A_at_B_high": 2 * (fit.params[1] + fit.params[3]),
    }
    alias = np.column_stack([design, a * b])
    assert np.linalg.matrix_rank(alias) == 4
    result = {
        **effects,
        "A_mean_ci95": (2 * fit.conf_int()[1]).tolist(),
        "interaction_difference": 4 * fit.params[3],
        "alias_rank": int(np.linalg.matrix_rank(alias)),
    }
    print("09 factorial effects:", result)
    return result


def case_10():
    # Two disconnected pairs. A unit's neighbor is its pair partner.
    neighbor = np.array([1, 0, 3, 2])
    baseline = np.arange(4, dtype=float)
    estimates = []
    for assignment in product([0, 1], repeat=4):
        a = np.array(assignment)
        g = a[neighbor]
        y = baseline + 2 * a + 3 * g
        # Bernoulli(1/2) assignment gives probability 1/4 to each (a,g) cell.
        means = {
            (own, other): np.mean(((a == own) & (g == other)) * y / 0.25)
            for own, other in product([0, 1], repeat=2)
        }
        estimates.append(
            [means[1, 0] - means[0, 0], means[0, 1] - means[0, 0], means[1, 1] - means[0, 0]]
        )
    direct, spillover, rollout = np.mean(estimates, axis=0)
    assert np.allclose([direct, spillover, rollout], [2, 3, 5])
    cluster = []
    for assignments in product([0, 1], repeat=2):
        a = np.repeat(assignments, 2)
        y = baseline + 2 * a + 3 * a[neighbor]
        cluster.append(np.mean(a * y / 0.5 - (1 - a) * y / 0.5))
    assert np.isclose(np.mean(cluster), rollout)
    result = {
        "mean_direct_estimator": direct,
        "mean_spillover_estimator": spillover,
        "mean_rollout_estimator": rollout,
        "cluster_policy_effect": np.mean(cluster),
        "individual_design_assignments": len(estimates),
        "cluster_assignments": len(cluster),
    }
    print("10 interference targets:", result)
    return result


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
    for case in (
        case_01,
        case_02,
        case_03,
        case_04,
        case_05,
        case_06,
        case_07,
        case_08,
        case_09,
        case_10,
        case_11,
        case_12,
    ):
        case()


if __name__ == "__main__":
    main()
