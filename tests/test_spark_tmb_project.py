"""Host bridge contracts and independent Gaussian integral oracles, without R."""

from __future__ import annotations

import copy
import importlib
import importlib.util
import math
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/advanced-spark-modeling/projects/spark-tmb"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
bridge = importlib.import_module("spark_tmb.fixed_bridge")


def rows() -> list[dict[str, Any]]:
    return [{"row_id": f"r{i}", "group_id": f"g{i // 2}", "y": float(i)} for i in range(6)]


def fake_r(request: Any, prepared: Any) -> Any:
    records = [
        {
            "row_id": str(i),
            "group_id": str(request["data"].get("group", [0] * len(request["data"]["y"]))[i]),
            "y": y,
        }
        for i, y in enumerate(request["data"]["y"])
    ]
    oracle = bridge.normal_oracle if request["model"] == "normal_mean" else bridge.laplace_oracle
    value, gradient = oracle(records, request["theta"])
    return value, gradient, {"R": "test-double", "TMB": "test-double", "source_md5": "test-double"}


def test_registry_boundary_and_no_object_serialization() -> None:
    request = bridge.request_for("normal_mean", rows(), [0.2, 0.3])
    assert request["theta"] == [0.2, 0.3]
    assert request["parameters"] == {"mu": 0.2, "log_sigma": 0.3}
    assert request["random"] is None
    random = bridge.request_for("random_intercept", rows(), [0.2, 0.3, 0.4])
    assert random["data"]["group"] == [0, 0, 1, 1, 2, 2]
    assert random["random"] == "u" and random["parameters"]["u"] == [0, 0, 0]


@pytest.mark.parametrize("bad", [[], [0], [0, 0, 0], [math.nan, 0], [True, 0]])
def test_bad_parameters_rejected(bad: Any) -> None:
    with pytest.raises((bridge.ObjectiveError, ValueError)):
        bridge.request_for("normal_mean", rows(), bad)


@pytest.mark.parametrize(
    "bad",
    [
        {"row_id": "", "group_id": "g", "y": 1},
        {"row_id": "r", "group_id": "g", "y": True},
        {"row_id": "r", "group_id": "g", "y": math.inf},
        {"row_id": "r", "group_id": "g", "y": "1"},
    ],
)
def test_invalid_rows_rejected(bad: Any) -> None:
    with pytest.raises(bridge.ObjectiveError):
        bridge.bounded_rows([bad])


def test_row_bound_consumes_only_bounded_iterator() -> None:
    def generator() -> Iterator[dict[str, Any]]:
        for i in range(bridge.MAX_ROWS + 2):
            yield {"row_id": str(i), "group_id": "g", "y": 1}
        raise AssertionError("An unbounded partition iterator was fully consumed")

    with pytest.raises(bridge.ObjectiveError, match="capacity"):
        bridge.bounded_rows(generator())


def test_membership_is_order_invariant_and_content_bound() -> None:
    original = rows()
    assert bridge.membership_digest(original) == bridge.membership_digest(list(reversed(original)))
    changed = copy.deepcopy(original)
    changed[0]["y"] = 99
    assert bridge.membership_digest(changed) != bridge.membership_digest(original)


def test_normal_closed_form_score_at_changed_parameters() -> None:
    value, gradient = bridge.normal_oracle(rows(), [1, math.log(2)])
    expected = sum((i - 1) ** 2 for i in range(6)) / 8 + 6 * math.log(2 * math.sqrt(2 * math.pi))
    assert value == pytest.approx(expected)
    assert gradient == pytest.approx((-9 / 4, 6 - 31 / 4))


def test_laplace_rank_one_formula_gradient_matches_finite_difference() -> None:
    theta = [0.7, math.log(0.8), math.log(0.5)]
    value, gradient = bridge.laplace_oracle(rows(), theta)
    numeric = []
    for j in range(3):
        plus, minus = theta.copy(), theta.copy()
        plus[j] += 1e-5
        minus[j] -= 1e-5
        numeric.append(
            (bridge.laplace_oracle(rows(), plus)[0] - bridge.laplace_oracle(rows(), minus)[0])
            / 2e-5
        )
    assert math.isfinite(value)
    assert gradient == pytest.approx(numeric, abs=1e-7)


def test_gaussian_marginal_reduces_to_independent_normals_as_tau_vanishes() -> None:
    records = rows()
    theta = [0.4, math.log(1.2)]
    marginal = bridge.laplace_oracle(records, [*theta, -20])
    normal = bridge.normal_oracle(records, theta)
    assert marginal[0] == pytest.approx(normal[0], abs=1e-10)
    assert marginal[1][:2] == pytest.approx(normal[1], abs=1e-10)


def test_partition_reduction_empty_and_stale_failures_use_detached_test_double() -> None:
    theta = [0.2, 0.3]
    original = rows()
    with patch.object(bridge, "evaluate_r", side_effect=fake_r):
        records = [
            bridge.partition_result(i, part, "normal_mean", theta)
            for i, part in enumerate([original[:2], original[2:], []])
        ]
    result = bridge.combine_results(
        records,
        parameters=theta,
        model="normal_mean",
        expected_rows=original,
        expected_partitions=3,
    )
    assert result.value == pytest.approx(bridge.normal_oracle(original, theta)[0])
    assert result.row_count == 6 and result.partition_count == 3
    with pytest.raises(bridge.ObjectiveError):
        bridge.combine_results(
            records,
            parameters=[0.3, 0.3],
            model="normal_mean",
            expected_rows=original,
            expected_partitions=3,
        )
    with pytest.raises(bridge.ObjectiveError):
        bridge.combine_results(
            [records[0], records[0], records[1]],
            parameters=theta,
            model="normal_mean",
            expected_rows=original,
            expected_partitions=3,
        )


def test_splitting_latent_groups_is_rejected_even_with_correct_row_count() -> None:
    theta = [0.2, 0.3, 0.4]
    original = rows()
    with patch.object(bridge, "evaluate_r", side_effect=fake_r):
        records = [
            bridge.partition_result(i, part, "random_intercept", theta)
            for i, part in enumerate([original[::2], original[1::2]])
        ]
    with pytest.raises(bridge.ObjectiveError, match="group was split"):
        bridge.combine_results(
            records,
            parameters=theta,
            model="random_intercept",
            expected_rows=original,
            expected_partitions=2,
        )


def test_model_name_never_becomes_arbitrary_code_or_path() -> None:
    for model in ("../model", "Rcode()", "ar1", "custom-unprepared"):
        with pytest.raises(bridge.ObjectiveError):
            bridge.request_for(model, rows(), [0, 0])


def registered_modules() -> Any:
    if str(PROJECT) not in sys.path:
        sys.path.insert(0, str(PROJECT))
    registry = importlib.import_module("spark_tmb.registry")
    runtime = importlib.import_module("spark_tmb.runtime")

    return registry, runtime


def test_registered_payload_custom_numeric_schema_and_layout() -> None:
    registry, _ = registered_modules()
    payload = registry.payload_for(
        PROJECT, "random_intercept", {"y": [1, 2, 3], "group": [0, 0, 1]}, [0.2, 0.3, 0.4]
    )
    assert payload["parameters"]["u"] == [0, 0]
    assert payload["random"] == "u"
    assert list(payload["parameters"]) == ["beta", "log_sigma", "log_tau", "u"]
    for data in (
        {"y": [1, 2], "group": [1, 1]},
        {"y": [1, 2], "group": [0, 0.5]},
        {"y": [1, 2], "group": [0]},
        {"y": [1, 2], "group": [0, 0], "R_code": "system()"},
    ):
        with pytest.raises(registry.ModelContractError):
            registry.payload_for(PROJECT, "random_intercept", data, [0, 0, 0])


def copy_registry(tmp_path: Path) -> dict[str, Any]:
    import json
    import shutil

    (tmp_path / "models").mkdir()
    shutil.copy(PROJECT / "registry.json", tmp_path / "registry.json")
    for path in (PROJECT / "models").glob("*.cpp"):
        shutil.copy(path, tmp_path / "models" / path.name)
    return cast(dict[str, Any], json.loads((tmp_path / "registry.json").read_text()))


@pytest.mark.parametrize(
    "field,value",
    [
        ("factorization", "coupled_latent"),
        ("source", "../../external.cpp"),
        ("fixed_parameters", ["mu", "mu"]),
        ("data", {"y": "arbitrary_R_code"}),
    ],
)
def test_registry_rejects_unprepared_factorization_paths_and_types(
    tmp_path: Path, field: Any, value: Any
) -> None:
    import json

    registry, _ = registered_modules()
    config = copy_registry(tmp_path)
    config["models"]["normal_mean"][field] = value
    (tmp_path / "registry.json").write_text(json.dumps(config))
    with pytest.raises(registry.ModelContractError):
        registry.load_registry(tmp_path)


def test_prepared_artifact_receipt_detects_changed_cpp_and_library(tmp_path: Path) -> None:
    import json

    registry, runtime = registered_modules()
    copy_registry(tmp_path)
    build = tmp_path / "compiled"
    build.mkdir()
    library = build / "normal_mean.so"
    library.write_bytes(b"a host fixture, not compiled code")
    receipt = {
        "schema_version": 1,
        "registry_sha256": registry.sha256(tmp_path / "registry.json"),
        "abi": {"R": "4.6.1", "TMB": "1.9.25", "Matrix": "1.7.6", "architecture": "fixture"},
        "models": {
            "normal_mean": {
                "library": "normal_mean.so",
                "library_sha256": registry.sha256(library),
                "source_sha256": registry.sha256(tmp_path / "models/normal_mean.cpp"),
            }
        },
    }
    (build / "receipt.json").write_text(json.dumps(receipt))
    assert runtime.verify_prepared(tmp_path, build, "normal_mean") == receipt
    library.write_bytes(b"changed library")
    with pytest.raises(registry.ModelContractError, match="library bytes"):
        runtime.verify_prepared(tmp_path, build, "normal_mean")
    library.write_bytes(b"a host fixture, not compiled code")
    (tmp_path / "models/normal_mean.cpp").write_text("// changed source")
    with pytest.raises(registry.ModelContractError, match=r"C\+\+ source"):
        runtime.verify_prepared(tmp_path, build, "normal_mean")


class LocalRDD:
    """Host-only Spark protocol test double, never execution evidence."""

    def __init__(self, partitions: Any) -> None:
        self.partitions = partitions

    def getNumPartitions(self) -> Any:
        return len(self.partitions)

    def mapPartitionsWithIndex(self, callback: Any) -> Any:
        class Collected:
            def collect(inner: Any) -> Any:
                return [
                    result
                    for i, partition in enumerate(self.partitions)
                    for result in callback(i, iter(partition))
                ]

        return Collected()


def test_prepared_spark_adapter_binds_data_and_driver_artifact() -> None:
    registered_modules()
    adapter = importlib.import_module("spark_tmb.spark")

    ModelContractError = importlib.import_module("spark_tmb.registry").ModelContractError

    units = [
        {"unit_id": "g0", "data": {"y": [1.0, 2.0, 4.0]}},
        {"unit_id": "g1", "data": {"y": [2.0, 5.0, 8.0]}},
    ]
    rdd = LocalRDD([[units[0]], [], [units[1]]])
    receipt = {
        "registry_sha256": "registry",
        "abi": {"R": "fixture"},
        "models": {"normal_mean": {"source_sha256": "source", "library_sha256": "library"}},
    }

    def fake_evaluation(model: Any, data: Any, theta: Any, **options: Any) -> Any:
        value, gradient = bridge.normal_oracle([{"y": v} for v in data["y"]], theta)
        return {
            "value": value,
            "gradient": gradient,
            "artifact_source_sha256": "source",
            "artifact_library_sha256": "library",
            "artifact_registry_sha256": "registry",
            "abi": {"R": "fixture"},
        }

    with (
        patch.object(adapter, "verify_prepared", return_value=receipt),
        patch.object(adapter, "evaluate_prepared", side_effect=fake_evaluation),
    ):
        objective = adapter.SparkTMBObjective(rdd, "normal_mean", root=PROJECT)
        result = objective.evaluate([0, 0])
        assert result.row_count == 6 and result.partition_count == 3
        rdd.partitions[0][0]["data"]["y"][0] = 99
        with pytest.raises(ModelContractError, match="data changed"):
            objective.evaluate([0, 0])
        rdd.partitions[0][0]["data"]["y"][0] = 1
        wrong = {
            **fake_evaluation("normal_mean", units[0]["data"], [0, 0]),
            "artifact_library_sha256": "wrong-but-consistent-worker-library",
        }
        with (
            patch.object(adapter, "evaluate_prepared", return_value=wrong),
            pytest.raises(ModelContractError, match="prepared artifacts"),
        ):
            objective.evaluate([0, 0])


def test_owned_registered_models_match_the_reviewed_tmb_curriculum_templates() -> None:
    original = ROOT / "courses/tmb-modeling/projects/tmb-local/models"
    for name in ("normal_mean", "random_intercept"):
        assert (PROJECT / "models" / (name + ".cpp")).read_bytes() == (
            original / (name + ".cpp")
        ).read_bytes()


@pytest.mark.parametrize("value", [-2147483647, 2147483647, 0, -1, 1, 2147483647.0])
def test_r_integer_bounds_preserve_exact_native_values(value: Any) -> None:
    registry, _ = registered_modules()
    assert registry.integer32(value) == value
    assert type(registry.integer32(value)) is int


@pytest.mark.parametrize(
    "value",
    [
        -2147483648,
        2147483648,
        9007199254740993,
        -9007199254740993,
        True,
        False,
        0.5,
        math.nan,
        math.inf,
        -math.inf,
        "1",
    ],
)
def test_r_integer_bounds_reject_before_float_conversion(value: Any) -> None:
    registry, _ = registered_modules()
    with pytest.raises(registry.ModelContractError):
        registry.integer32(value)


def test_all_supervisors_stop_real_sigterm_ignoring_descendants() -> None:
    registered_modules()
    check_processes = importlib.import_module("check_processes")

    result = check_processes.run_checks()
    assert len(result) == 6 and all(row["descendant_stopped"] for row in result)


def test_cli_describe_reuses_registry_and_artifact_validation() -> None:
    registered_modules()
    cli = importlib.import_module("spark_tmb.cli")
    runtime = importlib.import_module("spark_tmb.runtime")

    receipt = {
        "registry_sha256": "registry",
        "abi": {"R": "4.6.1"},
        "models": {"normal_mean": {"source_sha256": "source", "library_sha256": "library"}},
    }
    with (
        patch.object(runtime, "verify_prepared", return_value=receipt),
        patch.object(
            cli, "evaluate_prepared", side_effect=AssertionError("describe must not evaluate")
        ),
    ):
        result = cli.handle(
            {"schema_version": 1, "operation": "describe", "model_id": "normal_mean"}, root=PROJECT
        )
    assert result["result"]["spec"]["fixed_parameters"] == ["mu", "log_sigma"]
    assert result["result"]["prepared"]["library_sha256"] == "library"
    assert result["result"]["max_rows"] == 4096


@pytest.mark.parametrize(
    "payload",
    [
        '{"schema_version":1,"schema_version":1,"operation":"describe","model_id":"normal_mean"}',
        '{"schema_version":true,"operation":"describe","model_id":"normal_mean"}',
        '{"schema_version":1,"operation":"describe","model_id":"normal_mean","path":"/tmp/other"}',
        '{"schema_version":1,"operation":"evaluate","model_id":"normal_mean","data":{"y":[NaN]},"parameters":[0,0]}',
        "{}",
    ],
)
def test_cli_invalid_input_returns_bounded_error_without_success(payload: Any) -> None:
    import json
    import os
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "spark_tmb.cli"],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                [str(PROJECT), str(ROOT / "packages/spark-likelihood/src")]
            ),
        },
    )
    assert result.returncode == 2 and result.stdout == ""
    error = json.loads(result.stderr)
    assert error["schema_version"] == 1 and len(error["error"]["message"]) <= 2048


def test_typed_vector_parameter_layout_preserves_canonical_and_native_order() -> None:
    registry, _ = registered_modules()
    spec = registry.load_registry(PROJECT)["models"]["linear_regression"]
    assert spec["fixed_parameters"] == ["beta_0", "beta_1", "log_sigma"]
    assert spec["native_parameter_names"] == ["beta", "beta", "log_sigma"]
    request = registry.payload_for(
        PROJECT, "linear_regression", {"x": [0, 1], "y": [1, 3]}, [1, 2, -0.4]
    )
    assert request["parameters"] == {"beta": [1.0, 2.0], "log_sigma": -0.4}
    assert request["data"]["prediction_mode"] == 0 and request["data"]["x_prediction"] == []


def test_prediction_construction_has_no_response_inputs_or_invented_target() -> None:
    registry, _ = registered_modules()
    normal = registry.prediction_payload(PROJECT, "normal_location", {}, [2, 0], n_rows=3)
    assert normal["data"] == {"prediction_mode": 1, "y": [], "n_prediction": 3}
    regression = registry.prediction_payload(
        PROJECT, "linear_regression", {"x_prediction": [-1, 2]}, [1, 2, 0], n_rows=2
    )
    assert regression["data"]["x"] == regression["data"]["y"] == []
    assert regression["target"] == "conditional_mean"
    for model, data, theta, n in [
        ("normal_mean", {}, [0, 0], 2),
        ("normal_location", {"y": [1, 2]}, [0, 0], 2),
        ("linear_regression", {"x_prediction": [1]}, [0, 0, 0], 2),
    ]:
        with pytest.raises(registry.ModelContractError):
            registry.prediction_payload(PROJECT, model, data, theta, n_rows=n)
    with pytest.raises(registry.ModelContractError):
        registry.prediction_payload(
            PROJECT, "normal_location", {}, [0, 0], n_rows=2, target="observation_interval"
        )


def test_registry_rejects_prediction_label_leakage_and_dynamic_parameter_sizes(
    tmp_path: Path,
) -> None:
    import json

    registry, _ = registered_modules()
    config = copy_registry(tmp_path)
    config["models"]["linear_regression"]["prediction"]["from_training"]["x_prediction"] = "y"
    (tmp_path / "registry.json").write_text(json.dumps(config))
    with pytest.raises(registry.ModelContractError, match="response-free"):
        registry.load_registry(tmp_path)
    config["models"]["linear_regression"]["prediction"]["from_training"]["x_prediction"] = "x"
    config["models"]["linear_regression"]["parameter_layout"][0]["size"] = "infer_from_data"
    (tmp_path / "registry.json").write_text(json.dumps(config))
    with pytest.raises(registry.ModelContractError, match="parameter block"):
        registry.load_registry(tmp_path)


def test_prediction_schema_refuses_fabricated_labels_and_phase_type_changes(tmp_path: Path) -> None:
    import json

    registry, _ = registered_modules()
    config = copy_registry(tmp_path)
    prediction = config["models"]["normal_location"]["prediction"]
    prediction["constants"]["y"]["value"] = [0]
    (tmp_path / "registry.json").write_text(json.dumps(config))
    with pytest.raises(registry.ModelContractError, match="fabricate response"):
        registry.load_registry(tmp_path)
    prediction["constants"]["y"]["value"] = []
    prediction["constants"]["y"]["kind"] = "integer_vector"
    (tmp_path / "registry.json").write_text(json.dumps(config))
    with pytest.raises(registry.ModelContractError, match="native data field type"):
        registry.load_registry(tmp_path)


def test_rdd_evaluation_streams_one_unit_before_consuming_the_next() -> None:
    registered_modules()
    adapter = importlib.import_module("spark_tmb.spark")

    calls: list[str] = []

    def units() -> Any:
        yield {"unit_id": "a", "data": {"y": [1, 2]}}
        assert calls == ["evaluated"], "worker buffered raw units before evaluation"
        yield {"unit_id": "b", "data": {"y": [3, 4]}}

    def evaluate(*args: Any, **kwargs: Any) -> Any:
        calls.append("evaluated")
        return {
            "value": 1.0,
            "gradient": [0.0, 0.0],
            "artifact_source_sha256": "s",
            "artifact_library_sha256": "l",
            "artifact_registry_sha256": "r",
            "abi": {"R": "fixture"},
        }

    with patch.object(adapter, "evaluate_prepared", side_effect=evaluate):
        result = list(
            adapter._evaluate(
                0, units(), root=PROJECT, build_dir="/fixture", model_id="normal_mean", theta=[0, 0]
            )
        )
    assert calls == ["evaluated", "evaluated"]
    assert result[0]["metadata"]["rows"] == 4
    assert result[0]["summary"].value == 2
    assert "data" not in result[0]["metadata"]


def test_fixed_bridge_import_is_independent_of_legacy_bridge_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import ModuleType

    legacy = ModuleType("bridge")
    monkeypatch.setitem(sys.modules, "bridge", legacy)
    checks = importlib.import_module("check_processes")
    assert checks.PreparedTMB is bridge.PreparedTMB
    assert sys.modules["bridge"] is legacy
