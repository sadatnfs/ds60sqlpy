"""Reviewed numerical mechanisms for the statistical-learning tutorial route."""

import numpy as np
from scipy import optimize, special, stats
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import brier_score_loss, log_loss, mean_squared_error
from sklearn.model_selection import GridSearchCV, GroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor


def wilson_interval(successes, n, alpha=0.05):
    p = np.asarray(successes) / n
    z = stats.norm.ppf(1 - alpha / 2)
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


def case_01():
    n, successes = 12, 1
    estimate = successes / n
    score = successes / estimate - (n - successes) / (1 - estimate)
    information = n / (estimate * (1 - estimate))
    wald = estimate + np.array([-1, 1]) * stats.norm.ppf(0.975) / np.sqrt(information)
    wilson = wilson_interval(successes, n)
    assert abs(score) < 1e-10 and wald[0] < 0 and wilson[0] > 0
    # Exact enumeration of the sampling distribution, not a Monte Carlo claim.
    s = np.arange(n + 1)
    true_p = 0.05
    probability = stats.binom.pmf(s, n, true_p)
    phat = s / n
    half = stats.norm.ppf(0.975) * np.sqrt(phat * (1 - phat) / n)
    wl, wu = wilson_interval(s, n)
    wald_coverage = probability @ ((phat - half <= true_p) & (true_p <= phat + half))
    wilson_coverage = probability @ ((wl <= true_p) & (true_p <= wu))
    assert wilson_coverage > wald_coverage + 0.3
    result = {
        "mle": estimate,
        "score_at_mle": score,
        "information": information,
        "wald": wald.tolist(),
        "wilson": list(wilson),
        "exact_wald_coverage_at_005": wald_coverage,
        "exact_wilson_coverage_at_005": wilson_coverage,
    }
    print("01 likelihood to coverage:", result)
    return result


def logistic_objective(beta, design, outcome):
    eta = design @ beta
    return np.sum(np.logaddexp(0, eta) - outcome * eta)


def case_02():
    rng = np.random.default_rng(1102)
    x = rng.normal(size=(500, 2))
    design = np.column_stack([np.ones(len(x)), x])
    y = rng.binomial(1, special.expit(design @ np.array([-0.4, 1.0, -0.7])))
    train, test = np.arange(350), np.arange(350, 500)

    def objective(b):
        return logistic_objective(b, design[train], y[train])

    def gradient(b):
        return design[train].T @ (special.expit(design[train] @ b) - y[train])

    fit = optimize.minimize(objective, np.zeros(3), jac=gradient, method="BFGS")
    assert fit.success and np.linalg.norm(gradient(fit.x)) < 1e-4
    p = special.expit(design[train] @ fit.x)
    hessian = design[train].T @ ((p * (1 - p))[:, None] * design[train])
    covariance = np.linalg.solve(hessian, np.eye(3))
    se = np.sqrt(np.diag(covariance))
    test_p = special.expit(design[test] @ fit.x)
    threshold = 2 / (2 + 8)
    decisions = test_p > threshold
    cost = np.mean(2 * (decisions & (y[test] == 0)) + 8 * (~decisions & (y[test] == 1)))
    bins = np.digitize(test_p, [0.2, 0.4, 0.6, 0.8])
    calibration = [
        (
            int(b),
            int((bins == b).sum()),
            float(test_p[bins == b].mean()),
            float(y[test][bins == b].mean()),
        )
        for b in np.unique(bins)
    ]
    # Equal baseline strata in both arms: marginal and conditional OR can still differ.
    baseline = np.array([-2.0, 2.0])
    p0, p1 = special.expit(baseline).mean(), special.expit(baseline + np.log(2)).mean()
    marginal_or = p1 / (1 - p1) / (p0 / (1 - p0))
    assert 1 < marginal_or < 2
    separated = np.array([-2.0, -1.0, 1.0, 2.0])[:, None]
    labels = np.array([0, 0, 1, 1])
    assert logistic_objective([8], separated, labels) < logistic_objective([4], separated, labels)
    result = {
        "coefficients": fit.x.tolist(),
        "model_se": se.tolist(),
        "slope1_or_ci95": np.exp(fit.x[1] + np.array([-1, 1]) * 1.96 * se[1]).tolist(),
        "test_log_loss": log_loss(y[test], test_p),
        "test_brier": brier_score_loss(y[test], test_p),
        "cost_at_02": cost,
        "calibration_bins": calibration,
        "conditional_or": 2.0,
        "marginal_or": marginal_or,
    }
    print("02 logistic model to decision:", result)
    return result


def tree_fixture():
    rng = np.random.default_rng(1903)
    x = rng.normal(size=(360, 6))
    y = 3 * x[:, 0] + 2 * x[:, 1] ** 2 + rng.normal(scale=0.5, size=len(x))
    return x, y


def case_03():
    x, y = tree_fixture()
    results = []
    models = []
    for candidates in (1, 3, 6):
        for leaf in (2, 8):
            model = RandomForestRegressor(
                n_estimators=48,
                max_features=candidates,
                min_samples_leaf=leaf,
                oob_score=True,
                random_state=1903,
                n_jobs=1,
            ).fit(x[:180], y[:180])
            validation = mean_squared_error(y[180:270], model.predict(x[180:270]))
            results.append((candidates, leaf, validation))
            models.append(model)
    chosen = int(np.argmin([row[2] for row in results]))
    model = models[chosen]
    predictions = np.array([tree.predict(x[270:]) for tree in model.estimators_])
    errors = predictions - y[270:]
    correlation = np.corrcoef(errors)
    corr = correlation[np.triu_indices(len(predictions), 1)].mean()
    assert np.allclose(predictions.mean(axis=0), model.predict(x[270:]))
    bootstrap = np.random.default_rng(3).integers(0, 6, 6)
    oob = np.setdiff1d(np.arange(6), np.unique(bootstrap))
    assert not set(oob) & set(bootstrap)
    result = {
        "validation_candidates": results,
        "chosen": results[chosen][:2],
        "test_mse": mean_squared_error(y[270:], model.predict(x[270:])),
        "test_tree_error_correlation": corr,
        "oob_score": model.oob_score_,
        "tiny_bootstrap_indices": bootstrap.tolist(),
        "tiny_oob_indices": oob.tolist(),
    }
    print("03 forest selection:", result)
    return result


def case_04():
    x = np.arange(6, dtype=float)[:, None]
    y = np.array([0.0, 0.0, 0.0, 6.0, 6.0, 6.0])
    current = np.full(6, 3.0)
    losses = [mean_squared_error(y, current)]
    for _ in range(4):
        tree = DecisionTreeRegressor(max_depth=1, random_state=4).fit(x, y - current)
        current += 0.5 * tree.predict(x)
        losses.append(mean_squared_error(y, current))
    assert np.allclose(losses, 9 * 0.25 ** np.arange(5))
    labels = np.array([0, 0, 0, 1, 1, 1])
    score = np.zeros(6)
    p = special.expit(score)
    gradient, curvature = p - labels, p * (1 - p)
    left, right = x[:, 0] < 2.5, x[:, 0] >= 2.5
    weights = [-gradient[mask].sum() / (curvature[mask].sum() + 1) for mask in (left, right)]
    updated = np.where(left, weights[0], weights[1]) * 0.5
    assert log_loss(labels, special.expit(updated)) < log_loss(labels, p)
    features, target = tree_fixture()
    model = GradientBoostingRegressor(
        n_estimators=100, learning_rate=0.08, max_depth=2, random_state=4
    ).fit(features[:180], target[:180])
    validation = [
        mean_squared_error(target[180:270], prediction)
        for prediction in model.staged_predict(features[180:270])
    ]
    best = int(np.argmin(validation)) + 1
    frozen = GradientBoostingRegressor(
        n_estimators=best, learning_rate=0.08, max_depth=2, random_state=4
    ).fit(features[:180], target[:180])
    result = {
        "squared_loss_trace": losses,
        "logistic_leaf_weights": weights,
        "selected_stage": best,
        "validation_mse": validation[best - 1],
        "test_mse": mean_squared_error(target[270:], frozen.predict(features[270:])),
    }
    print("04 boosting trajectory:", result)
    return result


def case_05():
    # Balanced sign pairs make signal exactly orthogonal to the large nuisance.
    nuisance = np.linspace(-100, 100, 100)
    x = np.column_stack([np.repeat(nuisance, 2), np.tile([-0.1, 0.1], 100)])
    y = np.tile([0, 1], 100)
    test_x = np.column_stack([np.repeat(np.linspace(-95, 95, 40), 2), np.tile([-0.1, 0.1], 40)])
    test_y = np.tile([0, 1], 40)
    pca = PCA(n_components=1).fit(x)
    reconstruction = pca.inverse_transform(pca.transform(x))
    pca_model = make_pipeline(PCA(n_components=1), LogisticRegression()).fit(x, y)
    full_model = make_pipeline(StandardScaler(), LogisticRegression()).fit(x, y)
    assert pca.explained_variance_ratio_[0] > 0.9999
    assert pca_model.score(test_x, test_y) == 0.5 and full_model.score(test_x, test_y) == 1
    assert np.isclose(np.mean((x - reconstruction) ** 2), 0.005)
    centered = x - x.mean(axis=0)
    singular = np.linalg.svd(centered, compute_uv=False)
    assert np.isclose(np.sum((x - reconstruction) ** 2), singular[1] ** 2)
    scaled = PCA().fit(StandardScaler().fit_transform(x))
    result = {
        "raw_retained_variance": pca.explained_variance_ratio_[0],
        "reconstruction_mse": np.mean((x - reconstruction) ** 2),
        "pca_test_accuracy": pca_model.score(test_x, test_y),
        "full_test_accuracy": full_model.score(test_x, test_y),
        "scaled_variance_ratios": scaled.explained_variance_ratio_.tolist(),
    }
    print("05 compression versus prediction:", result)
    return result


def case_06():
    rng = np.random.default_rng(2206)
    groups = np.repeat(np.arange(60), 4)
    x = groups[:, None]
    y = np.repeat(rng.binomial(1, 0.5, 60), 4)
    model = make_pipeline(
        OneHotEncoder(handle_unknown="ignore", sparse_output=False), LogisticRegression(C=10)
    )
    row_scores = cross_val_score(model, x, y, cv=StratifiedKFold(4, shuffle=True, random_state=6))
    group_scores = cross_val_score(model, x, y, cv=GroupKFold(4), groups=groups)
    assert row_scores.mean() > group_scores.mean() + 0.2
    # A complete nested preprocessing/tuning workflow with group boundaries.
    features = rng.normal(size=(240, 3))
    target = features @ np.array([2.0, -1.0, 0.5]) + rng.normal(size=240)
    outer_scores = []
    for train, test in GroupKFold(3).split(features, target, groups):
        search = GridSearchCV(
            make_pipeline(StandardScaler(), Ridge()),
            {"ridge__alpha": [0.1, 1, 10]},
            cv=GroupKFold(3),
            scoring="neg_mean_squared_error",
        ).fit(features[train], target[train], groups=groups[train])
        assert np.allclose(search.best_estimator_[0].mean_, features[train].mean(axis=0))
        outer_scores.append(mean_squared_error(target[test], search.predict(features[test])))
    result = {
        "row_accuracy": row_scores.mean(),
        "new_group_accuracy": group_scores.mean(),
        "nested_outer_mse": outer_scores,
    }
    print("06 evaluation of the full procedure:", result)
    return result


def case_07():
    x = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
    y = np.array([1.0, 2.0, 4.0])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    assert np.allclose(beta, [5 / 6, 3 / 2]) and np.allclose(x.T @ residual, 0)
    hessian = x.T @ x
    eigenvalues = np.linalg.eigvalsh(hessian)
    at = np.array([0.2, 0.5])
    analytic = x.T @ (x @ at - y)
    difference = optimize.approx_fprime(at, lambda b: 0.5 * np.sum((x @ b - y) ** 2), 1e-7)
    assert np.allclose(analytic, difference, atol=1e-6)

    def descend(rate):
        b = np.zeros(2)
        for _ in range(30):
            b -= rate * (x.T @ (x @ b - y))
        return float(np.linalg.norm(b - beta))

    stable = descend(1 / eigenvalues[-1])
    unstable = descend(2.2 / eigenvalues[-1])
    assert stable < unstable
    result = {
        "beta": beta.tolist(),
        "residual": residual.tolist(),
        "hessian_eigenvalues": eigenvalues.tolist(),
        "gradient": analytic.tolist(),
        "stable_error": stable,
        "oversized_step_error": unstable,
    }
    print("07 geometry and optimization:", result)
    return result


def case_08():
    rng = np.random.default_rng(1908)
    n, delta = 1000, 0.05
    thresholds = np.linspace(0, 1, 41)  # Fixed before the sample.
    x = rng.uniform(size=n)
    y = rng.binomial(1, 0.2 + 0.6 * x)
    empirical = ((x[:, None] >= thresholds) != y[:, None]).mean(axis=0)
    risk = 0.5 - 0.6 * thresholds + 0.6 * thresholds**2
    radius = np.sqrt(np.log(2 * len(thresholds) / delta) / (2 * n))
    chosen = np.argmin(empirical)
    assert np.all(np.abs(empirical - risk) < radius)
    assert risk[chosen] - risk.min() <= 2 * radius
    # A fixed uniform prior and a data-dependent Gibbs posterior over finite rules.
    posterior = special.softmax(-20 * empirical)
    kl = np.sum(special.xlogy(posterior, posterior * len(thresholds)))
    rhs = (kl + np.log(2 * np.sqrt(n) / delta)) / n
    gibbs_empirical, gibbs_risk = posterior @ empirical, posterior @ risk
    upper = min(1.0, gibbs_empirical + np.sqrt(rhs / 2))
    assert kl >= 0 and gibbs_risk <= upper
    result = {
        "hypotheses": len(thresholds),
        "uniform_radius": radius,
        "selected_threshold": thresholds[chosen],
        "empirical_risk": empirical[chosen],
        "true_risk": risk[chosen],
        "oracle_risk": risk.min(),
        "gibbs_kl": kl,
        "gibbs_true_risk": gibbs_risk,
        "pac_bayes_upper": upper,
    }
    print("08 learning guarantees and assumptions:", result)
    return result


def main():
    for case in (case_01, case_02, case_03, case_04, case_05, case_06, case_07, case_08):
        case()


if __name__ == "__main__":
    main()
