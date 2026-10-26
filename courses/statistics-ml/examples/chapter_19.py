import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor


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

    def variance(b):
        return sigma2 * (rho + (1 - rho) / b)

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


def feature_sampling_comparison():
    rng = np.random.default_rng(1905)
    x = rng.normal(size=(240, 6))
    y = 3 * x[:, 0] + x[:, 1] ** 2 + rng.normal(scale=0.4, size=len(x))
    for candidates in (1, 6):
        forest = RandomForestRegressor(
            n_estimators=48,
            max_features=candidates,
            min_samples_leaf=3,
            bootstrap=True,
            oob_score=True,
            random_state=19,
            n_jobs=1,
        ).fit(x[:160], y[:160])
        predictions = np.array([tree.predict(x[160:]) for tree in forest.estimators_])
        errors = predictions - y[160:]
        correlation = np.corrcoef(errors)
        mean_correlation = correlation[np.triu_indices(len(predictions), 1)].mean()
        mse = np.mean((predictions.mean(axis=0) - y[160:]) ** 2)
        assert forest.estimators_[0].max_features_ == candidates
        assert np.allclose(predictions.mean(axis=0), forest.predict(x[160:]))
        print(
            "Candidate features:",
            candidates,
            "held-out MSE:",
            round(mse, 4),
            "tree error correlation:",
            round(mean_correlation, 4),
            "OOB R-squared:",
            round(forest.oob_score_, 4),
        )
    # Correlation and accuracy are measured separately; smaller subsets need not win.


def second_order_leaf():
    g = np.array([-2.0, -1.0])
    h = np.ones(2)
    penalty = 1.0
    weight = -g.sum() / (h.sum() + penalty)

    def objective(w):
        return g.sum() * w + 0.5 * (h.sum() + penalty) * w * w

    assert weight == 1 and objective(weight) < objective(0)
    assert np.isclose(g.sum() + (h.sum() + penalty) * weight, 0)
    print("Regularized Newton leaf weight:", weight)


def main():
    split_geometry()
    forest_and_variance()
    feature_sampling_comparison()
    boosting_update()
    second_order_leaf()


if __name__ == "__main__":
    main()
