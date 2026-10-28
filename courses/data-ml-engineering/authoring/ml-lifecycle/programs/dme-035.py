"""Fit transformations on training rows and inspect their learned state."""

import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ds60sqlpy.plot_artifacts import publish_report, publish_table


def training_data():
    return pd.DataFrame(
        {
            "hours": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0],
            "region": ["north", "south", "north", "south", "north", "south", "north", "south"],
        }
    ), np.array([0, 0, 0, 1, 0, 1, 1, 1])


def transformer():
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    category = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer([("numeric", numeric, ["hours"]), ("category", category, ["region"])])


def example_one():
    train, labels = training_data()
    pipeline = Pipeline(
        [("features", transformer()), ("model", LogisticRegression(random_state=35))]
    )
    pipeline.fit(train, labels)
    preprocessor = pipeline.named_steps["features"]
    numeric = preprocessor.named_transformers_["numeric"]
    original_median = float(numeric.named_steps["impute"].statistics_[0])
    original_mean = float(numeric.named_steps["scale"].mean_[0])
    future = pd.DataFrame({"hours": [np.nan, 1000.0, 4.0], "region": ["west", "north", np.nan]})
    transformed = preprocessor.transform(future)
    names = preprocessor.get_feature_names_out().tolist()
    assert original_median == 5.0
    assert original_mean == np.mean([1, 2, 5, 4, 5, 6, 7, 8])
    assert transformed.shape == (3, 3) and np.isfinite(transformed).all()
    assert np.array_equal(transformed[0, 1:], [0.0, 0.0])
    assert np.array_equal(transformed[2, 1:], [1.0, 0.0])
    assert numeric.named_steps["scale"].mean_[0] == original_mean
    assert pipeline.predict_proba(future).shape == (3, 2)
    return {
        "train_only_median": original_median,
        "train_only_imputed_mean": original_mean,
        "feature_names": names,
        "transformed_future": transformed.tolist(),
        "unknown_region_encoded_as_all_zero": True,
        "evaluation_refit_performed": False,
    }


def example_two():
    train, _ = training_data()
    future = pd.DataFrame({"hours": [1000.0, 2000.0], "region": ["west", "west"]})
    correct = transformer().fit(train)
    leaky = transformer().fit(pd.concat([train, future], ignore_index=True))
    correct_numeric = correct.named_transformers_["numeric"]
    leaky_numeric = leaky.named_transformers_["numeric"]
    correct_mean = float(correct_numeric.named_steps["scale"].mean_[0])
    leaky_mean = float(leaky_numeric.named_steps["scale"].mean_[0])
    assert np.isclose(correct_mean, 4.75) and np.isclose(leaky_mean, 303.9)
    original_names = correct.get_feature_names_out().tolist()
    leaked_names = leaky.get_feature_names_out().tolist()
    assert len(original_names) == 3 and len(leaked_names) == 4
    assert "category__region_west" not in original_names
    assert "category__region_west" in leaked_names
    # Transformation is allowed; learning future statistics or categories is the leak.
    assert correct.transform(future).shape == (2, 3)
    assert float(correct_numeric.named_steps["scale"].mean_[0]) == correct_mean
    return {
        "correct_training_mean": correct_mean,
        "leaky_combined_mean": leaky_mean,
        "correct_feature_names": original_names,
        "leaky_feature_names": leaked_names,
        "same_input_columns_did_not_imply_same_fitted_state": True,
    }


def main():
    first, second = example_one(), example_two()
    publish_table(
        ["future row", *first["feature_names"]],
        [[number, *row] for number, row in enumerate(first["transformed_future"], start=1)],
        description="Evaluation rows transformed using frozen training-only preprocessing",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="Fitted medians, scales and vocabulary under deliberate leakage",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-035: two fitted-transformation cases passed")


if __name__ == "__main__":
    main()
