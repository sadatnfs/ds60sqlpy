"""Pure DataFrame-boundary contracts; test doubles do not claim Spark execution."""

from __future__ import annotations

import copy
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

PROJECT = Path(__file__).resolve().parents[1] / "courses/advanced-spark-modeling/projects/spark-tmb"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
adapter = importlib.import_module("spark_tmb.dataframe")


def schema(**fields: str) -> SimpleNamespace:
    return SimpleNamespace(
        fields=[
            SimpleNamespace(name=name, dataType=SimpleNamespace(typeName=lambda value=kind: value))
            for name, kind in fields.items()
        ]
    )


def identity() -> dict[str, Any]:
    return {
        "source_sha256": "a" * 64,
        "library_sha256": "b" * 64,
        "registry_sha256": "c" * 64,
        "abi": {
            "R": "4.6.1",
            "TMB": "1.9.25",
            "Matrix": "1.7.6",
            "architecture": "aarch64-unknown-linux-gnu",
        },
    }


def test_bindings_reject_wrong_types_missing_and_ambiguous_columns() -> None:
    adapter.validate_bindings(
        schema(outcome="double", category="integer"),
        {"y": "real_vector", "g": "integer_vector"},
        {"y": "outcome", "g": "category"},
    )
    for actual, fields, columns in [
        (schema(y="string"), {"y": "real_vector"}, {"y": "y"}),
        (schema(y="long"), {"y": "integer_vector"}, {}),
        (schema(y="double"), {"y": "integer_vector"}, {"y": "y"}),
        (schema(Y="double", y="double"), {"y": "real_vector"}, {"y": "y"}),
    ]:
        with pytest.raises(adapter.ModelContractError):
            adapter.validate_bindings(actual, fields, columns)


@pytest.mark.parametrize("value", [None, True, float("nan"), float("inf")])
def test_nonfinite_and_missing_values_refused(value: Any) -> None:
    with pytest.raises(adapter.ModelContractError):
        adapter._number(value, "real_vector")


@pytest.mark.parametrize("value", [-2147483648, 2147483648, 1.0, True])
def test_integer_domain_preserves_exact_r_contract(value: Any) -> None:
    with pytest.raises(adapter.ModelContractError):
        adapter._number(value, "integer_vector")


def test_owned_group_buffer_rejects_oversized_units_without_splitting() -> None:
    value = ((("number", 0),), (1.0,))
    with pytest.raises(adapter.ModelContractError):
        adapter._append_group([value] * 4096, value)
    with pytest.raises(adapter.ModelContractError):
        adapter._merge_groups([value] * 3000, [value] * 1097)


def test_group_sort_and_tie_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter, "check_artifact", lambda *args: None)
    options = {
        "model_id": "group",
        "root": "owned",
        "build_dir": "owned",
        "expected": identity(),
        "names": ["y", "group"],
        "kinds": {"y": "real_vector", "group": "integer_vector"},
    }
    rows = [((("number", 2),), (3.0, 0)), ((("number", 1),), (2.0, 0))]
    actual = list(adapter._group_units(iter([("unit", rows)]), **options))
    assert actual == [{"unit_id": "unit", "data": {"y": [2.0, 3.0], "group": [0, 0]}}]
    with pytest.raises(adapter.ModelContractError, match="unique"):
        list(adapter._group_units(iter([("unit", [rows[0], rows[0]])]), **options))


def test_row_chunking_keeps_all_values_and_bounds_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter, "check_artifact", lambda *args: None)
    units = list(
        adapter._row_units(
            2,
            iter([(float(x),) for x in range(5)]),
            model_id="normal_location",
            root="owned",
            build_dir="owned",
            expected=identity(),
            names=["y"],
            kinds={"y": "real_vector"},
            batch_size=2,
        )
    )
    assert [len(x["data"]["y"]) for x in units] == [2, 2, 1]
    assert [v for x in units for v in x["data"]["y"]] == [0.0, 1.0, 2.0, 3.0, 4.0]
    assert len({x["unit_id"] for x in units}) == 3


def test_artifact_identity_copies_and_compares_every_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = identity()
    description = {"prepared": copy.deepcopy(expected)}
    copy_identity = adapter.artifact_identity(description)
    copy_identity["abi"]["R"] = "changed"
    assert description["prepared"]["abi"]["R"] == "4.6.1"
    for field in ("registry_sha256", "source_sha256", "library_sha256"):
        altered = copy.deepcopy(description)
        altered["prepared"][field] = "d" * 64
        monkeypatch.setattr(
            adapter.runtime,
            "describe_prepared",
            lambda *a, value=altered, **kw: value,
            raising=False,
        )
        with pytest.raises(adapter.ModelContractError, match="changed"):
            adapter.check_artifact("normal_location", expected, "owned", "owned")


def test_response_free_prediction_preserves_rows_and_rejects_artifact_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = identity()
    calls = []
    monkeypatch.setattr(adapter, "check_artifact", lambda *args: None)

    def predict(model_id: Any, data: Any, theta: Any, **options: Any) -> Any:
        calls.append((data, options["n_rows"]))
        return {
            "prediction": [2.0] * options["n_rows"],
            "target": "conditional_mean",
            "nobs": options["n_rows"],
            "artifact_source_sha256": expected["source_sha256"],
            "artifact_library_sha256": expected["library_sha256"],
            "artifact_registry_sha256": expected["registry_sha256"],
            "abi": expected["abi"],
        }

    monkeypatch.setattr(adapter.runtime, "predict_prepared", predict, raising=False)
    options = {
        "model_id": "normal_location",
        "theta": (2.0, 0.0),
        "root": "owned",
        "build_dir": "owned",
        "expected": expected,
        "target": "conditional_mean",
        "inputs": {},
        "indices": {},
        "batch_size": 2,
    }
    rows = [("id-b", "text"), ("id-a", "other"), ("id-c", "last")]
    assert list(adapter._predict_partition(iter(rows), **options)) == [(*row, 2.0) for row in rows]
    assert calls == [({}, 2), ({}, 1)]
    corrupted = copy.deepcopy(expected)
    corrupted["registry_sha256"] = "f" * 64
    with pytest.raises(adapter.ModelContractError, match="changed"):
        list(adapter._predict_partition(iter(rows), **{**options, "expected": corrupted}))


def test_undeclared_target_and_output_overwrite_are_refused() -> None:
    with pytest.raises(adapter.ModelContractError, match="no declared"):
        adapter.prediction_bindings(
            schema(id="string"), {"prediction": None}, {}, "prediction", None
        )
    spec = {"prediction": {"target": "conditional_mean", "inputs": {}, "from_training": {}}}
    with pytest.raises(adapter.ModelContractError):
        adapter.prediction_bindings(schema(Prediction="double"), spec, {}, "prediction", None)
    with pytest.raises(adapter.ModelContractError):
        adapter.prediction_bindings(schema(id="string"), spec, {}, "prediction", "latent_mode")
