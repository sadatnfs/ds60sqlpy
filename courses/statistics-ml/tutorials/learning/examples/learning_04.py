"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import special
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import log_loss, mean_squared_error
from sklearn.tree import DecisionTreeRegressor


def tree_fixture():
    rng = np.random.default_rng(1903)
    x = rng.normal(size=(360, 6))
    y = 3 * x[:, 0] + 2 * x[:, 1] ** 2 + rng.normal(scale=0.5, size=len(x))
    return x, y


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


def main():
    case_04()


if __name__ == "__main__":
    main()
