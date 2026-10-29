"""Lightweight schema/ownership contracts, without Spark or Torch execution."""

from dataclasses import replace
from types import SimpleNamespace

import pytest
from ds60_spark_likelihood import dataframe as adapter
from ds60_spark_likelihood.contracts import ObjectiveError
from ds60_spark_likelihood.registry import resolve_model


def schema(**fields):
    return SimpleNamespace(
        fields=[
            SimpleNamespace(name=name, dataType=SimpleNamespace(typeName=lambda value=kind: value))
            for name, kind in fields.items()
        ]
    )


def test_explicit_features_reject_missing_wrong_or_ambiguous_types():
    model = resolve_model("linear_gaussian", {"feature_count": 2})
    adapter.feature_bindings(schema(a="double", b="long"), model, {"x0": "a", "x1": "b"})
    for actual, columns in [
        (schema(a="double"), {"x0": "a"}),
        (schema(a="string", b="double"), {"x0": "a", "x1": "b"}),
        (schema(a="double", A="double"), {"x0": "a", "x1": "A"}),
        (schema(a="double"), {"x0": "a", "x1": "a"}),
    ]:
        with pytest.raises(ObjectiveError):
            adapter.feature_bindings(actual, model, columns)


def test_integer_group_id_does_not_pass_through_float64():
    assert str(2**53 + 1) in adapter._identity(2**53 + 1)
    assert adapter._identity(1) != adapter._identity("1")
    with pytest.raises(ObjectiveError):
        adapter._identity(True)


def test_joint_weights_are_constant_and_not_summed_per_row():
    a = (2.0, None, (1.0,))
    b = (2.0, None, (3.0,))
    group = adapter._append_group(adapter._new_group(a), b, limit=2)
    assert group[0] == 2.0 and len(group[1]) == 2
    with pytest.raises(ObjectiveError, match="constant"):
        adapter._append_group(group, (3.0, None, (4.0,)), limit=3)
    with pytest.raises(ObjectiveError, match="may not be split"):
        adapter._append_group(group, b, limit=2)
    with pytest.raises(ObjectiveError, match="may not be split"):
        adapter._merge_groups(group, adapter._new_group(b), limit=2)


def test_complete_unit_ordering_and_duplicates():
    model = resolve_model("gaussian_random_intercept")
    descriptor = model.descriptor()
    rows = [((("number", 2),), (3.0,)), ((("number", 1),), (1.0,))]
    units = list(
        adapter._complete_units(
            iter([("group", (2.0, rows))]), model=model, descriptor=descriptor, ordered=True
        )
    )
    assert units[0].rows == ((1.0,), (3.0,)) and units[0].weight == 2.0
    with pytest.raises(ObjectiveError, match="unique"):
        list(
            adapter._complete_units(
                iter([("group", (1.0, [rows[0], rows[0]]))]),
                model=model,
                descriptor=descriptor,
                ordered=True,
            )
        )
    unordered = list(
        adapter._complete_units(
            iter([("group", (1.0, [(None, (3.0,)), (None, (1.0,))]))]),
            model=model,
            descriptor=descriptor,
            ordered=False,
        )
    )
    assert unordered[0].rows == ((1.0,), (3.0,))


def test_temporal_unit_requires_declared_order_before_spark_execution():
    model = replace(resolve_model("gaussian_random_intercept"), requires_order=True)
    frame = SimpleNamespace(schema=schema(y="double", group="string"))
    with pytest.raises(ObjectiveError, match="requires explicit"):
        adapter.DataFrameObjective(
            frame, model, feature_columns={}, label_col="y", group_col="group"
        )


def test_worker_guard_rejects_different_source_identity_before_math():
    model = resolve_model("normal_mean")
    bad = model.descriptor()
    bad["fingerprint"] = "0" * 64
    with pytest.raises(ObjectiveError, match="source/configuration"):
        adapter._row_guard(None, None, None, model=model, descriptor=bad)
    unit = resolve_model("gaussian_random_intercept")
    with pytest.raises(ObjectiveError):
        adapter._unit_guard(None, None, None, model=unit, descriptor=bad)


def test_prediction_does_not_extract_labels_and_preserves_rows(monkeypatch):
    model = resolve_model("normal_mean")
    calls = []

    def prediction(model, theta, features, target):
        calls.append((features, target))
        return [2.0] * len(features)

    monkeypatch.setattr(adapter, "predict_batch", prediction)
    rows = [("b", 99.0), ("a", -99.0), ("c", 5.0)]
    result = list(
        adapter._predict_rows(
            iter(rows),
            model=model,
            descriptor=model.descriptor(),
            theta=(2.0, 0.0),
            indices=[],
            target="conditional_mean",
            batch_size=2,
        )
    )
    assert result == [(*row, 2.0) for row in rows]
    assert calls == [([(), ()], "conditional_mean"), ([()], "conditional_mean")]


def test_group_population_target_is_not_a_conditional_group_prediction():
    model = resolve_model("gaussian_random_intercept")
    assert (
        adapter.prediction_schema(schema(id="string"), model, {}, "prediction") == "new_group_mean"
    )
    with pytest.raises(ObjectiveError, match="does not declare"):
        adapter.prediction_schema(
            schema(id="string"), model, {}, "prediction", "conditional_group_mean"
        )
    with pytest.raises(ObjectiveError, match="new simple"):
        adapter.prediction_schema(schema(Prediction="double"), model, {}, "prediction")


def test_raw_integer_observation_is_checked_before_float_conversion():
    with pytest.raises(ObjectiveError):
        adapter._group_pair((2**53 + 1, "group"), width=1, order_count=0, weighted=False)
