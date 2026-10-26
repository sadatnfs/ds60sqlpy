"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV, GroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


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


def main():
    case_06()


if __name__ == "__main__":
    main()
