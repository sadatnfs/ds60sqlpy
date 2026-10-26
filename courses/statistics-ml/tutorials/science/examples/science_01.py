"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import special
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold


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


def main():
    case_01()


if __name__ == "__main__":
    main()
