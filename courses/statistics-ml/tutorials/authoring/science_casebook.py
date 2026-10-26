"""Connected scientific workflows with explicit statistical evidence boundaries."""

import hashlib
import json

import numpy as np
import pandas as pd
from scipy import optimize, special, stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold
from statsmodels.duration.hazard_regression import PHReg


def aipw_score(a, y, e, m0, m1):
    return m1 - m0 + a * (y - m1) / e - (1 - a) * (y - m0) / (1 - e)


def case_01():
    rng = np.random.default_rng(1701)
    n = 1200
    x = rng.uniform(-2, 2, size=(n, 2))
    e = special.expit(0.6 * x[:, 0])
    a = rng.binomial(1, e)
    m0 = x[:, 0] ** 2 + x[:, 1]
    tau = 1 + 0.5 * x[:, 0]
    y = m0 + a * tau + rng.normal(size=n)
    eh, m0h, m1h = np.empty(n), np.empty(n), np.empty(n)
    for train, test in KFold(3, shuffle=True, random_state=17).split(x):
        propensity = LogisticRegression(C=100).fit(x[train], a[train])
        eh[test] = propensity.predict_proba(x[test])[:, 1]
        for arm, destination in ((0, m0h), (1, m1h)):
            arm_rows = train[a[train] == arm]
            model = RandomForestRegressor(
                n_estimators=48, min_samples_leaf=12, random_state=17, n_jobs=1
            ).fit(x[arm_rows], y[arm_rows])
            destination[test] = model.predict(x[test])
    assert np.all((eh > 0.05) & (eh < 0.95))
    score = aipw_score(a, y, eh, m0h, m1h)
    estimate, se = score.mean(), score.std(ddof=1) / np.sqrt(n)
    # Algebraic conditional bias checks, with truth available only in this fixture.
    bias_cases = {}
    for propensity_correct in (True, False):
        for outcome_correct in (True, False):
            ep = e if propensity_correct else np.full(n, 0.5)
            d0 = np.zeros(n) if outcome_correct else 0.8 * x[:, 0]
            d1 = np.zeros(n) if outcome_correct else 0.4 * x[:, 0]
            bias = np.mean((ep - e) * (d1 / ep + d0 / (1 - ep)))
            bias_cases[str((propensity_correct, outcome_correct))] = float(bias)
            if propensity_correct or outcome_correct:
                assert np.isclose(bias, 0)
    assert abs(bias_cases["(False, False)"]) > 0.1
    sensitivity = {str(bias): float(estimate - bias) for bias in (0, 0.25, 0.5, 1.0)}
    result = {
        "cross_fitted_ate": estimate,
        "score_se": se,
        "ci95": (estimate + np.array([-1, 1]) * 1.96 * se).tolist(),
        "population_ate": 1.0,
        "propensity_range": [eh.min(), eh.max()],
        "conditional_bias_cases": bias_cases,
        "assumed_bias_sensitivity": sensitivity,
    }
    print("01 causal estimation and sensitivity:", result)
    return result


def case_02():
    # Known group/noise variances isolate posterior calculation from MCMC.
    means = np.array([-1.0, 0.2, 1.4])
    sizes = np.array([2, 10, 30])
    prior_mean, tau2, sigma2 = 0.0, 1.0, 4.0
    posterior_variance = 1 / (1 / tau2 + sizes / sigma2)
    weight = sizes * tau2 / (sigma2 + sizes * tau2)
    posterior_mean = weight * means + (1 - weight) * prior_mean
    predictive_sd = np.sqrt(posterior_variance + sigma2)
    assert np.all(np.diff(weight) > 0) and np.all(predictive_sd > np.sqrt(posterior_variance))
    rng = np.random.default_rng(1802)
    draws = rng.normal(posterior_mean, np.sqrt(posterior_variance), size=(6000, 3))
    predictive = draws + rng.normal(0, np.sqrt(sigma2), size=draws.shape)
    assert np.allclose(predictive.var(axis=0), predictive_sd**2, rtol=0.07)
    narrow_prior = (sizes / sigma2 * means) / (1 / 0.25 + sizes / sigma2)
    # Posterior expected shortage cost at a candidate action, not just parameter means.
    action = 2.0
    loss = 4 * np.maximum(predictive - action, 0) + np.maximum(action - predictive, 0)
    result = {
        "unpooled_means": means.tolist(),
        "pooling_weights": weight.tolist(),
        "posterior_means": posterior_mean.tolist(),
        "posterior_sd": np.sqrt(posterior_variance).tolist(),
        "predictive_sd": predictive_sd.tolist(),
        "narrow_prior_means": narrow_prior.tolist(),
        "expected_asymmetric_loss_at_2": loss.mean(axis=0).tolist(),
    }
    print("02 posterior, prediction and decision:", result)
    return result


def seasonal_design(t):
    t = np.asarray(t)
    return np.column_stack(
        [np.ones(len(t)), t, np.sin(2 * np.pi * t / 12), np.cos(2 * np.pi * t / 12)]
    )


def case_03():
    rng = np.random.default_rng(2703)
    t = np.arange(60)
    series = np.array(
        [
            10
            + level
            + trend * t
            + 3 * np.sin(2 * np.pi * t / 12)
            + rng.normal(scale=0.4, size=len(t))
            for level, trend in ((0, 0.1), (4, 0.2), (-2, 0.05))
        ]
    )
    baseline_losses, model_losses = [], []
    for origin in range(24, 55, 6):
        train = np.arange(origin - 1)  # Label at t becomes available at t+2.
        future = np.arange(origin, origin + 3)
        assert np.max(train + 2) <= origin
        for values in series:
            beta = np.linalg.lstsq(seasonal_design(train), values[train], rcond=None)[0]
            forecast = seasonal_design(future) @ beta
            baseline = values[train[-1]]
            model_losses.extend((forecast - values[future]) ** 2)
            baseline_losses.extend((baseline - values[future]) ** 2)
    assert np.mean(model_losses) < np.mean(baseline_losses)
    revisions = pd.DataFrame(
        {"event": [10, 10, 11], "available": [12, 20, 13], "value": [1, 99, 2]}
    )
    asof = (
        revisions[revisions.available <= 15]
        .sort_values("available")
        .drop_duplicates("event", keep="last")
    )
    assert asof.set_index("event").loc[10, "value"] == 1
    result = {
        "rolling_model_rmse": np.sqrt(np.mean(model_losses)),
        "rolling_last_value_rmse": np.sqrt(np.mean(baseline_losses)),
        "forecast_count": len(model_losses),
        "asof_values": asof.value.tolist(),
    }
    print("03 vintage-aware forecasting:", result)
    return result


def cumulative_incidence(time, cause):
    survival, cif = 1.0, 0.0
    for at in np.unique(time):
        risk = np.sum(time >= at)
        d1 = np.sum((time == at) & (cause == 1))
        all_events = np.sum((time == at) & (cause != 0))
        cif += survival * d1 / risk
        survival *= 1 - all_events / risk
    return cif


def case_04():
    rng = np.random.default_rng(2804)
    n = 400
    x = rng.binomial(1, 0.5, n)
    event = rng.exponential(scale=1 / (0.12 * np.exp(np.log(1.7) * x)))
    censor = rng.exponential(scale=15, size=n)
    observed = np.minimum(event, censor)
    status = event <= censor
    cox = PHReg(observed, x[:, None], status=status).fit()
    assert np.isfinite(cox.params[0]) and cox.bse[0] > 0
    # Separate lognormal AFT generating model, fitted with censoring likelihood.
    true_log_time = 1 + 0.5 * x + rng.normal(scale=0.6, size=n)
    lifetime = np.exp(true_log_time)
    limit = rng.exponential(scale=8, size=n)
    t, died = np.minimum(lifetime, limit), lifetime <= limit

    def objective(parameters):
        location = parameters[0] + parameters[1] * x
        sigma = np.exp(parameters[2])
        z = (np.log(t) - location) / sigma
        contribution = np.where(
            died, stats.norm.logpdf(z) - np.log(t) - np.log(sigma), stats.norm.logsf(z)
        )
        return -contribution.sum()

    aft = optimize.minimize(objective, [1, 0, np.log(0.8)], method="BFGS", options={"gtol": 1e-4})
    assert aft.success and abs(aft.x[1] - 0.5) < 0.2
    times, causes = np.array([1, 2, 3, 4]), np.array([2, 1, 2, 1])
    cif = cumulative_incidence(times, causes)
    naive_survival = (1 - 1 / 3) * (1 - 1 / 1)
    assert np.isclose(cif, 0.5) and 1 - naive_survival > cif
    result = {
        "cox_hazard_ratio": np.exp(cox.params[0]),
        "cox_hr_ci95": np.exp(cox.conf_int()[0]).tolist(),
        "aft_time_ratio": np.exp(aft.x[1]),
        "true_aft_time_ratio": np.exp(0.5),
        "event_fraction": status.mean(),
        "cause1_cif": cif,
        "incorrect_cause1_km_risk": 1 - naive_survival,
    }
    print("04 censoring and competing events:", result)
    return result


def case_05():
    relevance = np.array([3, 2, 0, 1])
    order = np.array([1, 0, 3, 2])
    discount = 1 / np.log2(np.arange(2, 6))
    dcg = ((2 ** relevance[order] - 1) * discount).sum()
    ideal = ((2 ** np.sort(relevance)[::-1] - 1) * discount).sum()
    assert 0 < dcg / ideal < 1
    rng = np.random.default_rng(3205)
    n = 2000
    context = rng.integers(0, 2, n)
    action = rng.binomial(1, 0.2, n)
    reward_probability = np.where(action == context, 0.7, 0.3)
    reward = rng.binomial(1, reward_probability)
    logging_probability = np.where(action == 1, 0.2, 0.8)
    policy = context
    score = (action == policy) * reward / logging_probability
    estimate, se = score.mean(), score.std(ddof=1) / np.sqrt(n)
    assert abs(estimate - 0.7) < 4 * se
    value = np.array([3.0, 1.8, 2.0])
    cost = np.array([2.0, 1.0, 2.0])
    allocation = optimize.linprog(
        -value, A_ub=[cost], b_ub=[3], bounds=[(0, 1)] * 3, method="highs"
    )
    conservative = optimize.linprog(
        -(value - [1.5, 0.2, 0.1]), A_ub=[cost], b_ub=[3], bounds=[(0, 1)] * 3, method="highs"
    )
    assert allocation.success and conservative.success
    assert cost @ allocation.x <= 3 + 1e-8 and not np.allclose(allocation.x, conservative.x)
    result = {
        "ndcg": dcg / ideal,
        "ips_policy_value": estimate,
        "ips_se": se,
        "oracle_policy_value": 0.7,
        "expected_value_allocation": allocation.x.tolist(),
        "conservative_allocation": conservative.x.tolist(),
    }
    print("05 ranking, exposure and constrained action:", result)
    return result


def random_effects(effect, se):
    effect, se = np.asarray(effect), np.asarray(se)
    fixed_weights = 1 / se**2
    fixed = fixed_weights @ effect / fixed_weights.sum()
    q = np.sum(fixed_weights * (effect - fixed) ** 2)
    c = fixed_weights.sum() - np.sum(fixed_weights**2) / fixed_weights.sum()
    tau2 = max(0, (q - (len(effect) - 1)) / c)
    weights = 1 / (se**2 + tau2)
    mean = weights @ effect / weights.sum()
    hk_scale = max(1.0, np.sum(weights * (effect - mean) ** 2) / (len(effect) - 1))
    mean_se = np.sqrt(hk_scale / weights.sum())
    interval = mean + np.array([-1, 1]) * stats.t.ppf(0.975, len(effect) - 1) * mean_se
    prediction = mean + np.array([-1, 1]) * stats.t.ppf(0.975, len(effect) - 2) * np.sqrt(
        tau2 + mean_se**2
    )
    return mean, tau2, interval, prediction


def case_06():
    effect, se = np.array([0.1, 0.3, 0.8, 1.0, -0.2]), np.array([0.1, 0.15, 0.2, 0.18, 0.12])
    mean, tau2, interval, prediction = random_effects(effect, se)
    leave_one_out = [random_effects(np.delete(effect, i), np.delete(se, i))[0] for i in range(5)]
    assert tau2 > 0 and np.ptp(prediction) > np.ptp(interval)
    # A scale transformation must also transform uncertainty.
    converted = random_effects(100 * effect, 100 * se)
    assert np.isclose(converted[0], 100 * mean) and np.isclose(converted[1], 10000 * tau2)
    result = {
        "mean_effect": mean,
        "tau_squared": tau2,
        "modified_hk_ci95": interval.tolist(),
        "approximate_prediction_interval": prediction.tolist(),
        "leave_one_out_means": leave_one_out,
    }
    print("06 synthesis and heterogeneity:", result)
    return result


def case_07():
    rng = np.random.default_rng(4007)
    n = 360
    event_time = np.arange(n)
    available = event_time + 3
    x = rng.normal(size=n)
    y = rng.binomial(1, special.expit(1.8 * x))
    cutoff = 240
    train = available <= cutoff
    test = (event_time > cutoff) & (available <= 320)
    assert np.all(available[train] <= cutoff) and not np.any(train & test)
    model = LogisticRegression().fit(x[train, None], y[train])
    prediction = model.predict_proba(x[test, None])[:, 1]
    reference_loss = log_loss(y[test], prediction)
    leaked_available = event_time + 10
    feature_allowed = leaked_available <= event_time
    assert not feature_allowed.any()  # A future-derived label feature is excluded.
    record = {
        "definition": "logistic-one-predictor-v1",
        "label_delay": 3,
        "cutoff": cutoff,
        "train_rows": int(train.sum()),
        "test_rows": int(test.sum()),
        "coefficient": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
    }
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    identity = hashlib.sha256(encoded).hexdigest()
    shifted_x = rng.normal(size=500)
    shifted_y = rng.binomial(1, special.expit(-1.8 * shifted_x))
    shifted_loss = log_loss(shifted_y, model.predict_proba(shifted_x[:, None])[:, 1])
    safe_baseline_loss = log_loss(shifted_y, np.full(len(shifted_y), 0.5))
    action = "rollback candidate" if shifted_loss > safe_baseline_loss + 0.1 else "continue review"
    assert action == "rollback candidate" and len(identity) == 64
    result = {
        "artifact_identity": identity,
        "record": record,
        "held_out_log_loss": reference_loss,
        "shifted_log_loss": shifted_loss,
        "baseline_log_loss": safe_baseline_loss,
        "decision": action,
    }
    print("07 scientific workflow evidence:", result)
    return result


def case_08():
    rng = np.random.default_rng(1708)
    n = 30000
    l0 = rng.binomial(1, 0.5, n)
    e0 = special.expit(-0.4 + 0.8 * l0)
    a0 = rng.binomial(1, e0)
    l1 = rng.binomial(1, special.expit(l0 - a0))
    e1 = special.expit(-0.4 + l1)
    a1 = rng.binomial(1, e1)
    y = 1 + 2 * a0 + 3 * a1 + l0 + l1 + rng.normal(size=n)
    regime_means = []
    oracle = []
    for regime in (0, 1):
        probability = np.where(regime == 1, e0, 1 - e0) * np.where(regime == 1, e1, 1 - e1)
        assert np.all((probability > 0) & (probability < 1))
        consistent = (a0 == regime) & (a1 == regime)
        regime_means.append(np.mean(consistent * y / probability))
        oracle.append(1 + 5 * regime + 0.5 + np.mean(special.expit(np.array([0, 1]) - regime)))
    effect, true_effect = np.diff(regime_means)[0], np.diff(oracle)[0]
    assert abs(effect - true_effect) < 0.2 and true_effect < 5
    result = {
        "sustained_regime_ipw_means": regime_means,
        "oracle_regime_means": oracle,
        "ipw_total_effect": effect,
        "oracle_total_effect": true_effect,
        "controlled_direct_coefficient_sum": 5.0,
    }
    print("08 treatment-confounder feedback:", result)
    return result


def case_09():
    # Deliberately separate profile: PyMC 5.28.5 and ArviZ 0.23.4 InferenceData.
    import arviz as az
    import pymc as pm

    rng = np.random.default_rng(1809)
    group = np.repeat(np.arange(6), [3, 5, 8, 10, 12, 15])
    truth = np.array([-1.2, -0.4, 0.0, 0.6, 1.0, 1.5])
    y = truth[group] + rng.normal(scale=1.0, size=len(group))
    with pm.Model(coords={"group": np.arange(6), "observation": np.arange(len(y))}):
        mu = pm.Normal("mu", mu=0, sigma=2)
        tau = pm.HalfNormal("tau", sigma=1)
        z = pm.Normal("z", mu=0, sigma=1, dims="group")
        theta = pm.Deterministic("theta", mu + tau * z, dims="group")
        sigma = pm.HalfNormal("sigma", sigma=2)
        pm.Normal("outcome", mu=theta[group], sigma=sigma, observed=y, dims="observation")
        prior = pm.sample_prior_predictive(samples=200, random_seed=1809)
        fitted = pm.sample(
            draws=600,
            tune=600,
            chains=2,
            cores=1,
            random_seed=1809,
            target_accept=0.95,
            progressbar=False,
            return_inferencedata=True,
        )
        predictive = pm.sample_posterior_predictive(
            fitted, var_names=["outcome"], random_seed=1810, progressbar=False
        )
    assert isinstance(fitted, az.InferenceData)
    summary = az.summary(fitted, var_names=["mu", "tau", "sigma", "theta"], kind="all")
    assert {"r_hat", "ess_bulk", "ess_tail", "mcse_mean"} <= set(summary.columns)
    divergences = int(fitted.sample_stats.diverging.sum())
    posterior_predictive = predictive.posterior_predictive["outcome"].values
    prior_predictive = prior.prior_predictive["outcome"].values
    assert posterior_predictive.shape[-1] == len(y) and np.isfinite(posterior_predictive).all()
    result = {
        "versions": {"pymc": pm.__version__, "arviz": az.__version__},
        "posterior_group_means": fitted.posterior.theta.mean(("chain", "draw")).values.tolist(),
        "observed_group_means": [float(y[group == g].mean()) for g in range(6)],
        "max_rhat": float(summary.r_hat.max()),
        "min_bulk_ess": float(summary.ess_bulk.min()),
        "divergences": divergences,
        "prior_predictive_sd": float(prior_predictive.std()),
        "posterior_predictive_sd": float(posterior_predictive.std()),
        "observed_sd": float(y.std(ddof=1)),
    }
    print("09 PyMC hierarchy and diagnostic evidence:", result)
    print(summary.to_string())
    return result


def main():
    # Default scientific environment never imports optional probabilistic packages.
    for case in (case_01, case_02, case_03, case_04, case_05, case_06, case_07, case_08):
        case()


if __name__ == "__main__":
    main()
