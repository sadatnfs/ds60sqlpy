import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
from sklearn.linear_model import Ridge
import statsmodels.api as sm


def ordinary_least_squares():
    x = np.arange(6, dtype=float)
    design = np.column_stack([np.ones(6), x])
    y = 1 + 2 * x + np.array([1.0, -1.0, 0.0, 0.0, -1.0, 1.0])
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    assert np.allclose(beta, [1, 2])
    assert np.allclose(design.T @ (y - design @ beta), 0)
    print("OLS intercept/slope:", beta)


def logistic_likelihood():
    x = np.column_stack([np.ones(8), np.arange(8) - 3.5])
    y = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
    objective = lambda b: np.sum(np.logaddexp(0, x @ b) - y * (x @ b))
    gradient = lambda b: x.T @ (expit(x @ b) - y)
    fit = minimize(objective, np.zeros(2), jac=gradient, method="BFGS")
    assert fit.success and np.linalg.norm(gradient(fit.x)) < 1e-4
    assert objective(fit.x) < objective(np.zeros(2))
    doubled_odds_probability = expit(np.log(0.2 / 0.8) + np.log(2))
    assert np.isclose(doubled_odds_probability, 1 / 3)
    print("Logistic coefficients:", fit.x, "twice odds probability:", doubled_odds_probability)


def counts_with_exposure():
    exposure = np.array([1.0, 2.0, 3.0, 4.0])
    counts = np.array([2.0, 5.0, 5.0, 8.0])
    fit = sm.GLM(
        counts, np.ones((4, 1)), family=sm.families.Poisson(), offset=np.log(exposure)
    ).fit()
    estimated_rate = np.exp(fit.params[0])
    assert np.isclose(estimated_rate, counts.sum() / exposure.sum())
    assert np.allclose(fit.predict(offset=np.log(exposure)), 2 * exposure)
    print("Exposure-adjusted Poisson rate:", estimated_rate)


def shrinkage():
    x = np.array([[-2.0], [-1.0], [0.0], [1.0], [2.0]])
    y = 3 * x[:, 0]
    ridge = Ridge(alpha=10, fit_intercept=False).fit(x, y)
    assert np.isclose(ridge.coef_[0], 1.5)
    print("Unpenalized slope 3; ridge slope:", ridge.coef_[0])


def main():
    ordinary_least_squares()
    logistic_likelihood()
    counts_with_exposure()
    shrinkage()


if __name__ == "__main__":
    main()
