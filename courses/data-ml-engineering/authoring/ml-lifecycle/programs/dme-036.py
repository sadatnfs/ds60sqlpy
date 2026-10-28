"""Use one fitted pipeline behind a typed, unit-aware JSON inference boundary."""

import json
import math

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ds60sqlpy.plot_artifacts import publish_report, publish_table

FEATURES = ["hours", "region"]
UNITS = {"hours": "hours", "region": "category"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonfinite JSON constant is not allowed")


def validated_frame(raw):
    if type(raw) is not str or len(raw.encode("utf-8")) > 2048:
        raise ValueError("Use bounded UTF-8 JSON text")
    try:
        request = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (ValueError, RecursionError) as error:
        raise ValueError("Invalid strict JSON request") from error
    if type(request) is not dict or set(request) != {"schema_version", "units", "features"}:
        raise ValueError("Unexpected request fields")
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise ValueError("Incompatible schema version")
    if request["units"] != UNITS:
        raise ValueError("Incompatible feature units")
    features = request["features"]
    if type(features) is not dict or set(features) != set(FEATURES):
        raise ValueError("Missing or unexpected feature names")
    hours = features["hours"]
    if type(hours) not in {int, float} or not 0 <= hours <= 1000:
        raise ValueError("Hours must be a bounded number, not a boolean or text")
    if not math.isfinite(hours):
        raise ValueError("Hours must be finite")
    if type(features["region"]) is not str or features["region"] not in {"north", "south"}:
        raise ValueError("Region is outside this deployed model's closed contract")
    # JSON object order is immaterial. Construct the model's named input order.
    return pd.DataFrame([[float(hours), features["region"]]], columns=FEATURES)


class Predictor:
    def __init__(self):
        train = pd.DataFrame(
            {"hours": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], "region": ["north", "south"] * 4}
        )
        transforms = ColumnTransformer(
            [
                ("numeric", StandardScaler(), ["hours"]),
                ("category", OneHotEncoder(handle_unknown="error"), ["region"]),
            ]
        )
        self.model = Pipeline(
            [("features", transforms), ("model", LogisticRegression(random_state=36))]
        )
        self.model.fit(train, [0, 0, 0, 1, 0, 1, 1, 1])
        self.calls = 0

    def score_json(self, raw):
        frame = validated_frame(raw)
        self.calls += 1
        return float(self.model.predict_proba(frame)[0, 1])


def request(hours=7, region="north"):
    return {
        "schema_version": 1,
        "units": UNITS.copy(),
        "features": {"hours": hours, "region": region},
    }


def example_one():
    predictor = Predictor()
    raw = json.dumps(request())
    direct = float(
        predictor.model.predict_proba(pd.DataFrame([[7.0, "north"]], columns=FEATURES))[0, 1]
    )
    served = predictor.score_json(raw)
    reordered = request()
    reordered["features"] = {"region": "north", "hours": 7}
    served_reordered = predictor.score_json(json.dumps(reordered))
    assert np.allclose([served, served_reordered], direct, rtol=0, atol=1e-12)
    return {
        "direct_probability": direct,
        "interface_probability": served,
        "reordered_json_probability": served_reordered,
        "interface_prediction_calls": predictor.calls,
        "one_fitted_pipeline": True,
    }


def example_two():
    predictor = Predictor()
    cases = []
    changed_units = request()
    changed_units["units"] = {"hours": "minutes", "region": "category"}
    changed_schema = request()
    changed_schema["schema_version"] = 2
    missing = request()
    del missing["features"]["region"]
    for name, value in [
        ("changed units", changed_units),
        ("changed version", changed_schema),
        ("missing feature", missing),
        ("boolean number", request(True)),
        ("unknown region", request(region="west")),
        ("huge integer", request(10**400)),
    ]:
        cases.append((name, json.dumps(value)))
    valid_raw = json.dumps(request())
    assert valid_raw.count('"schema_version": 1') == 1
    assert valid_raw.count('"hours": 7') == 1
    cases.append(
        (
            "duplicate field",
            valid_raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1),
        )
    )
    cases.append(("nonfinite constant", valid_raw.replace('"hours": 7', '"hours": NaN', 1)))
    rejected = []
    for name, raw in cases:
        try:
            predictor.score_json(raw)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError("An incompatible request reached the model: " + name)
    assert predictor.calls == 0 and len(rejected) == 8
    return {
        "rejected_cases": rejected,
        "interface_prediction_calls": predictor.calls,
        "rejection_occurred_before_prediction": True,
    }


def main():
    first, second = example_one(), example_two()
    publish_table(
        ["path", "positive probability"],
        [
            ["direct fitted pipeline", first["direct_probability"]],
            ["validated JSON interface", first["interface_probability"]],
            ["reordered JSON fields", first["reordered_json_probability"]],
        ],
        description="The same actual fitted pipeline through three equivalent named-input paths",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="Schema, units, finite types and field validation before model execution",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-036: two train-serve interface cases passed")


if __name__ == "__main__":
    main()
