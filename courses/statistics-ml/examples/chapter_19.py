import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


def split_geometry():
    x = np.arange(6, dtype=float)[:, None]
    y = np.array([0.0, 0.0, 0.0, 6.0, 6.0, 6.0])
    stump = DecisionTreeRegressor(max_depth=1, random_state=19).fit(x, y)
    assert np.allclose(stump.predict(x), y)
    assert np.isclose(stump.tree_.threshold[0], 2.5)
    print(
        "Stump split:",
        stump.tree_.threshold[0],
        "training MSE:",
        np.mean((stump.predict(x) - y) ** 2),
    )


def forest_and_variance():
    x = np.linspace(0, 1, 80)[:, None]
    y = np.where(x[:, 0] < 0.5, 0.0, 2.0)
    forest = RandomForestRegressor(n_estimators=40, max_depth=3, random_state=19, n_jobs=1).fit(
        x, y
    )
    predictions = forest.predict([[0.1], [0.9]])
    assert np.allclose(predictions, [0.0, 2.0])
    rho, sigma2 = 0.3, 4.0
    variance = lambda b: sigma2 * (rho + (1 - rho) / b)
    assert variance(100) < variance(10) and variance(100) > rho * sigma2
    print(
        "Forest predictions:",
        predictions,
        "ensemble variance B10/B100:",
        variance(10),
        variance(100),
    )


def boosting_update():
    x = np.arange(6, dtype=float)[:, None]
    y = np.array([0.0, 0.0, 0.0, 6.0, 6.0, 6.0])
    current = np.full(len(y), y.mean())
    residual = y - current
    tree = DecisionTreeRegressor(max_depth=1, random_state=19).fit(x, residual)
    updated = current + 0.5 * tree.predict(x)
    before = np.mean((y - current) ** 2)
    after = np.mean((y - updated) ** 2)
    assert before == 9 and after == 2.25
    print("One half-step boosting MSE:", before, "to", after)


def second_order_leaf():
    g = np.array([-2.0, -1.0])
    h = np.ones(2)
    penalty = 1.0
    weight = -g.sum() / (h.sum() + penalty)
    objective = lambda w: g.sum() * w + 0.5 * (h.sum() + penalty) * w * w
    assert weight == 1 and objective(weight) < objective(0)
    assert np.isclose(g.sum() + (h.sum() + penalty) * weight, 0)
    print("Regularized Newton leaf weight:", weight)


def main():
    split_geometry()
    forest_and_variance()
    boosting_update()
    second_order_leaf()


if __name__ == "__main__":
    main()
