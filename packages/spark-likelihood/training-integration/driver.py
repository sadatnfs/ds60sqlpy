"""Run one explicitly selected Spark/Torch case in the owned Compose driver."""

from __future__ import annotations

import json
import socket
import struct
import traceback
from pathlib import Path

from ds60_torch_training import checkpoint, data
from ds60_torch_training._integration_fixture import gated_mlp_model
from ds60_torch_training.launch import run_training
from ds60_torch_training.observer import ProbeObserver
from ds60_torch_training.program import TrainingProgram
from ds60_torch_training.training_examples import linear_sgd_oracle, mlp_adam_example
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, LongType, StructField, StructType

SHARED = Path("/shared")
ATTEMPTS = SHARED / "attempts"
HELDOUT_FEATURES = [[1.0, -0.25], [1.0, 0.75], [1.0, 1.25]]


def _observer() -> ProbeObserver:
    return ProbeObserver(
        probe_jar="/probe/probe.jar",
        probe_manifest="/probe/probe.json",
        probe_source="/integration/Probe.scala",
    )


def _rows(labels: list[int], weights: list[int] | None = None, *, mlp: bool = False) -> list[dict]:
    weights = [1] * len(labels) if weights is None else weights
    return [
        {
            "id": index,
            "features": ([1.0, index / 10.0] if mlp else [1.0]),
            "label": float(label),
            "weight": float(weights[index]),
        }
        for index, label in enumerate(labels)
    ]


def _snapshot(
    name: str, labels: list[int], weights: list[int] | None = None, *, mlp: bool = False
) -> Path:
    path = SHARED / name / "manifest.json"
    if path.exists():
        data.load_manifest(path)
        return path
    return data.prepare_rows(
        _rows(labels, weights, mlp=mlp),
        path.parent,
        feature_names=["x0", "x1"] if mlp else ["x"],
        num_shards=6,
        source_metadata={"case": name, "split": "train", "row_source": "fixed-6-v1"},
    )


def _assignment(path: Path, world: int) -> dict:
    manifest = data.load_manifest(path)
    files = [row["path"] for row in manifest["files"]]
    return data.assign_shards(
        manifest,
        world,
        rank_files=[files] if world == 1 else [files[:4], files[4:]],
    )


def _program(*, mlp: bool = False):
    if not mlp:
        return linear_sgd_oracle()
    ordinary = mlp_adam_example()
    return TrainingProgram(
        model_factory=gated_mlp_model,
        loss_factory=ordinary.loss_factory,
        optimizer_factory=ordinary.optimizer_factory,
        feature_names=ordinary.feature_names,
        configuration=ordinary.configuration,
        precision=ordinary.precision,
        target_domain=ordinary.target_domain,
        code_modules=("ds60_torch_training._integration_fixture",),
    )


def _checkpoint_reference(root: Path) -> checkpoint.CheckpointRef:
    committed = sorted(root.glob("*/COMMITTED.json"))
    if len(committed) != 1:
        raise RuntimeError("Expected exactly one committed epoch before fault")
    marker = json.loads(committed[0].read_text())
    return checkpoint.CheckpointRef(
        path=str(committed[0].parent),
        manifest_digest=marker["manifest_digest"],
        transaction_digest=marker["transaction_digest"],
    )


def _run(
    spark,
    path: Path,
    name: str,
    *,
    world: int,
    epochs: int,
    mlp: bool = False,
    resume=None,
) -> dict:
    return run_training(
        spark,
        _program(mlp=mlp),
        path,
        mode="executor_single" if world == 1 else "executor_ddp",
        world_size=world,
        assignment=_assignment(path, world),
        epochs=epochs,
        steps_per_epoch=1,
        max_batch_rows=32768,
        seed=2026,
        output_dir=ATTEMPTS / name,
        observer=_observer(),
        timeout_seconds=120,
        resume=resume,
    )


def _state(reference: dict, rank: int):
    manifest = json.loads((Path(reference["path"]) / "manifest.json").read_text())
    return checkpoint.load_rank(
        Path(reference["path"]),
        expected_binding=manifest["binding"],
        expected_manifest_digest=reference["manifest_digest"],
        rank=rank,
    )


def _compare_continuation(reference: dict, resumed: dict) -> dict:
    matching = []
    final_pair = None
    for rank in (0, 1):
        left = _state(reference, rank)
        right = _state(resumed, rank)
        if left.binding != right.binding or left.progress != right.progress:
            raise AssertionError("Reference and resumed binding/progress differ")
        if left.state != right.state or left.ledger != right.ledger:
            raise AssertionError("Reference and resumed tensor/optimizer/RNG/data state differ")
        matching.append(rank)
        if rank == 0:
            final_pair = (left, right)

    def predict(loaded):
        import numpy as np
        import torch

        recipe = mlp_adam_example()
        model = gated_mlp_model(recipe.configuration["model"])
        state = {}
        for name, item in loaded.state["model"].items():
            if item.dtype != "float64":
                raise AssertionError("Held-out inference needs the declared float64 state")
            array = np.frombuffer(item.data, dtype="<f8").copy().reshape(item.shape)
            state[name] = torch.from_numpy(array)
        model.load_state_dict(state, strict=True)
        model.eval()
        with torch.no_grad():
            logits = model(torch.tensor(HELDOUT_FEATURES, dtype=torch.float64)).reshape(-1)
            return [float(item) for item in torch.sigmoid(logits)]

    assert final_pair is not None
    left_scores, right_scores = map(predict, final_pair)
    if left_scores != right_scores or len(left_scores) != len(HELDOUT_FEATURES):
        raise AssertionError("Response-free held-out scores differ after explicit recovery")
    return {
        "exact_continuation_ranks": matching,
        "heldout_prediction": {
            "scope": "local checkpoint inference in the owned driver container",
            "conditioning": "fixed response-free features, binary sigmoid, eval mode, float64",
            "feature_names": ["x0", "x1"],
            "features": HELDOUT_FEATURES,
            "probabilities": left_scores,
            "exact_reference_resume_equality": True,
        },
    }


def _oracle_parameter(reference: dict, target: float) -> dict:
    loaded = _state(reference, 0)
    state = loaded.state["model"]
    observed = {}
    for name in ("weight", "bias"):
        tensor = state[name]
        if tensor.dtype != "float64" or len(tensor.data) != 8:
            raise AssertionError("Oracle parameter layout changed")
        value = struct.unpack("<d", tensor.data)[0]
        if abs(value - target) > 1e-12:
            raise AssertionError("Global weighted mean oracle parameter differs")
        observed[name] = value
    return observed


def main() -> None:
    selection = json.loads((SHARED / "current-case.json").read_text())
    case = selection["case"]
    ATTEMPTS.mkdir(exist_ok=True)
    spark = SparkSession.builder.getOrCreate()
    report = {"schema_version": 1, "case": case, "status": "failed"}
    try:
        if case == "single":
            basic = _snapshot("snapshot-basic", [0, 1, 1, 0, 1, 1])
            weighted = _snapshot("snapshot-weighted", [0, 1, 1, 0, 1, 0], [1, 3, 1, 0, 2, 1])
            _snapshot("snapshot-mlp", [0, 1, 1, 0, 1, 1], mlp=True)
            results = {}
            for name, path in (("basic", basic), ("weighted", weighted)):
                for world in (1, 2):
                    key = f"{name}-{world}"
                    results[key] = _run(spark, path, key, world=world, epochs=1)
            report["attempts"] = {
                key: value["worker_result"]["latest_checkpoint"] for key, value in results.items()
            }
            report["oracle_parameters"] = {
                key: _oracle_parameter(
                    value["worker_result"]["latest_checkpoint"],
                    1 / 60 if key.startswith("basic") else 1 / 40,
                )
                for key, value in results.items()
            }
            report["status"] = "passed"
        elif case == "reference":
            path = SHARED / "snapshot-mlp" / "manifest.json"
            report["latest_checkpoint"] = _run(
                spark, path, "mlp-reference", world=2, epochs=2, mlp=True
            )["worker_result"]["latest_checkpoint"]
            report["status"] = "passed"
        elif case == "fault":
            path = SHARED / "snapshot-mlp" / "manifest.json"
            try:
                _run(
                    spark,
                    path,
                    "mlp-fault",
                    world=2,
                    epochs=2,
                    mlp=True,
                )
            except Exception as error:  # noqa: BLE001 - expected controlled failed attempt
                report["controlled_failure"] = {
                    "type": type(error).__name__,
                    "message": str(error)[:2000],
                }
                report["resume_from"] = vars(
                    _checkpoint_reference(ATTEMPTS / "mlp-fault" / "checkpoints")
                )
                report["status"] = "expected_failure"
            else:
                raise AssertionError("Worker loss unexpectedly completed training")
        elif case == "resume":
            path = SHARED / "snapshot-mlp" / "manifest.json"
            fault = json.loads((SHARED / "fault-report.json").read_text())
            reference = json.loads((SHARED / "reference-report.json").read_text())
            result = _run(
                spark,
                path,
                "mlp-resume",
                world=2,
                epochs=2,
                mlp=True,
                resume=fault["resume_from"],
            )
            resumed = result["worker_result"]["latest_checkpoint"]
            report["continuation"] = _compare_continuation(reference["latest_checkpoint"], resumed)
            report["latest_checkpoint"] = resumed
            report["status"] = "passed"
        elif case == "dataframe":
            schema = StructType(
                [
                    StructField("id", LongType(), nullable=False),
                    StructField("x", DoubleType(), nullable=False),
                    StructField("y", DoubleType(), nullable=False),
                    StructField("w", DoubleType(), nullable=False),
                ]
            )
            rows = [
                (index, 1.0, float(label), float(weight))
                for index, (label, weight) in enumerate(
                    zip([0, 1, 1, 0, 1, 0], [1, 3, 1, 0, 2, 1], strict=True)
                )
            ]
            frame = spark.createDataFrame(rows, schema=schema)
            manifest_path = data.prepare_dataframe(
                frame,
                SHARED / "snapshot-dataframe",
                feature_names=["x"],
                label_col="y",
                id_col="id",
                weight_col="w",
                num_shards=2,
                source_metadata={
                    "case": "dataframe",
                    "split": "train",
                    "row_source": "fixed-6-typed-spark-v1",
                },
            )
            manifest = data.load_manifest(manifest_path)
            if (
                manifest["rows"] != 6
                or manifest["weight_sum"] != 8.0
                or manifest["feature_names"] != ["x"]
                or manifest["label_kind"] != "float"
                or len(manifest["files"]) != 2
            ):
                raise AssertionError("Executor DataFrame snapshot lost rows or weight mass")
            assignment = data.assign_shards(manifest, 2)

            def verify_rank(rank):
                from ds60_torch_training import data as worker_data

                labels = [0, 1, 1, 0, 1, 0]
                weights = [1, 3, 1, 0, 2, 1]
                mask = count = 0
                weight_sum = 0.0
                for row in worker_data.iter_rank_rows(manifest_path, assignment, rank):
                    row_id = row["id"]
                    if (
                        type(row_id) is not int
                        or not 0 <= row_id < 6
                        or row["features"] != [1.0]
                        or row["label"] != float(labels[row_id])
                        or row["weight"] != float(weights[row_id])
                    ):
                        raise AssertionError("Executor snapshot row/schema differs")
                    if mask & (1 << row_id):
                        raise AssertionError("Duplicate executor snapshot row ID")
                    mask |= 1 << row_id
                    count += 1
                    weight_sum += row["weight"]
                return {
                    "rank": rank,
                    "id_mask": mask,
                    "rows": count,
                    "weight_sum": weight_sum,
                    "hostname": socket.gethostname(),
                }

            coverage = spark.sparkContext.parallelize([0, 1], 2).map(verify_rank).collect()
            if (
                len(coverage) != 2
                or {row["rank"] for row in coverage} != {0, 1}
                or coverage[0]["id_mask"] & coverage[1]["id_mask"]
                or coverage[0]["id_mask"] | coverage[1]["id_mask"] != 63
                or sum(row["rows"] for row in coverage) != 6
                or sum(row["weight_sum"] for row in coverage) != 8.0
                or len({row["hostname"] for row in coverage}) != 2
            ):
                raise AssertionError("Executor metadata did not prove exact six-ID coverage")
            result = run_training(
                spark,
                linear_sgd_oracle(),
                manifest_path,
                mode="executor_ddp",
                world_size=2,
                assignment=assignment,
                epochs=1,
                steps_per_epoch=1,
                seed=2026,
                output_dir=ATTEMPTS / "dataframe-ddp",
                observer=_observer(),
                timeout_seconds=120,
            )
            reference = result["worker_result"]["latest_checkpoint"]
            report["snapshot"] = {
                "dataset_digest": manifest["dataset_digest"],
                "rows": manifest["rows"],
                "weight_sum": manifest["weight_sum"],
                "files": manifest["files"],
                "assignment_digest": assignment["assignment_digest"],
            }
            report["executor_coverage_metadata"] = coverage
            report["oracle_parameters"] = _oracle_parameter(reference, 1 / 40)
            report["status"] = "passed"
        else:
            raise RuntimeError("Unknown case")
    except Exception as error:  # noqa: BLE001 - retain bounded failed case receipt
        report["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
        report["traceback_tail"] = traceback.format_exc()[-4000:]
    finally:
        spark.stop()
        report_path = SHARED / (case + "-report.json")
        pending = report_path.with_suffix(".pending")
        pending.write_text(json.dumps(report, sort_keys=True) + "\n")
        pending.replace(report_path)
    if report["status"] == "expected_failure":
        raise SystemExit(17)
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
