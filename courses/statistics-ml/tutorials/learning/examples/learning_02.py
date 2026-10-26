"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import optimize, special
from sklearn.metrics import brier_score_loss, log_loss


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


def main():
    case_02()


if __name__ == "__main__":
    main()
