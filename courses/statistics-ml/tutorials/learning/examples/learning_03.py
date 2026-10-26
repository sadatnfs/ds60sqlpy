"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


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


def main():
    case_03()


if __name__ == "__main__":
    main()
