# SPDX-License-Identifier: Apache-2.0
"""Explicit public TorchDistributor executor launch with independent admission.

This module never installs dependencies, creates/stops Spark, or silently resumes
an attempt. Worker completion is provisional until listener evidence validates.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from . import checkpoint, data
from .contracts import (
    MAX_RECEIPT,
    TrainingError,
    canonical_json,
    digest,
    exact_keys,
    finite,
    integer,
    require_sha,
    write_new_json,
)
from .observer import MAX_OBSERVATION_BYTES, validate_evidence
from .program import TrainingProgram, schedule

GROUP_PROPERTIES = (
    "spark.jobGroup.id",
    "spark.job.description",
    "spark.job.interruptOnCancel",
)
MODES = {"executor_single": 1, "executor_ddp": 2}


def _runtime_identity() -> dict:
    from .runner import runtime_identity

    return runtime_identity()


def _require_prepared_wrapper() -> dict:
    from ds60_spark_likelihood.integrations.prepare_spark import (
        require_prepared_wrapper,
    )

    return require_prepared_wrapper()


def _distributor_class():
    from pyspark.ml.torch.distributor import TorchDistributor

    return TorchDistributor


def _worker():
    from .runner import _run_rank

    return _run_rank


def _spark_admission(spark, mode, world):
    if type(mode) is not str or mode not in MODES:
        raise TrainingError("Choose executor_single or executor_ddp explicitly")
    integer(world, "world_size", MODES[mode], MODES[mode])
    if getattr(spark, "_jsparkSession", None) is None:
        raise TrainingError("Training requires an existing Spark Classic session")
    context = spark.sparkContext
    if getattr(context, "_jsc", None) is None:
        raise TrainingError("Missing active Classic Spark context")
    master = context.master
    if (
        type(master) is not str
        or not master
        or master == "local"
        or master.startswith(("local[", "local-cluster["))
    ):
        raise TrainingError("Executor training refuses local masters")
    if str(spark.version) != "4.0.1" or str(context.version) != "4.0.1":
        raise TrainingError("Only prepared Spark 4.0.1 is admitted")
    conf = context.getConf()
    requirements = {
        "spark.task.maxFailures": (None, "1"),
        "spark.executor.cores": (None, "1"),
        "spark.task.cpus": ("1", "1"),
        "spark.speculation": ("false", "false"),
        "spark.dynamicAllocation.enabled": ("false", "false"),
    }
    for name, (default, expected) in requirements.items():
        if conf.get(name, default) != expected:
            raise TrainingError("Unsupported training setting: " + name)
    for name, value in conf.getAll():
        if ".resource.gpu." in name and str(value) not in ("", "0", "0.0"):
            raise TrainingError("CPU executor mode refuses GPU resource settings")
    return context


def _owned_path(path) -> Path:
    path = Path(path).absolute()
    if ".." in path.parts:
        raise TrainingError("Owned paths cannot contain parent traversal")
    for item in (path, *path.parents):
        if item.is_symlink():
            raise TrainingError("Owned paths cannot traverse symlinks")
    return path


def _reference(value):
    if value is None:
        return None
    if type(value) is checkpoint.CheckpointRef:
        value = asdict(value)
    exact_keys(
        value,
        {"path", "manifest_digest", "transaction_digest", "training_run_status"},
        name="checkpoint reference",
    )
    if (
        type(value["path"]) is not str
        or not Path(value["path"]).is_absolute()
        or value["training_run_status"] != "not_attested"
    ):
        raise TrainingError(
            "Require an explicit committed checkpoint reference without a success claim"
        )
    _owned_path(value["path"])
    require_sha(value["manifest_digest"])
    require_sha(value["transaction_digest"])
    return dict(value)


def _checkpoint_metadata(
    reference: dict, plan: dict, *, module_schema_digest: str | None = None
) -> dict:
    """Read committed identity/progress metadata, never tensor state on driver."""
    root = _owned_path(reference["path"])
    marker = checkpoint.read_json(root / "COMMITTED.json", allow_links=True)
    exact_keys(
        marker,
        {"schema_version", "kind", "manifest_digest", "transaction_digest"},
        name="checkpoint marker",
    )
    integer(marker["schema_version"], "checkpoint version", 1, 1)
    if (
        marker["kind"] != checkpoint.COMMIT_KIND
        or marker["manifest_digest"] != reference["manifest_digest"]
        or marker["transaction_digest"] != reference["transaction_digest"]
    ):
        raise TrainingError("Checkpoint marker/reference mismatch")
    raw = checkpoint.read_bytes(root / "manifest.json", checkpoint.MAX_JSON)
    if checkpoint.sha(raw) != reference["manifest_digest"]:
        raise TrainingError("Checkpoint manifest differs from explicit reference")
    manifest = checkpoint.parse_json(raw)
    exact_keys(
        manifest,
        {
            "schema_version",
            "kind",
            "transaction_digest",
            "binding",
            "progress",
            "ranks",
            "training_run_status",
        },
        name="checkpoint manifest",
    )
    integer(manifest["schema_version"], "checkpoint version", 1, 1)
    if (
        manifest["kind"] != "torch_training_checkpoint_manifest_v1"
        or manifest["training_run_status"] != "not_attested"
        or manifest["transaction_digest"] != reference["transaction_digest"]
    ):
        raise TrainingError("Unknown committed checkpoint manifest")
    binding = checkpoint.validate_binding(manifest["binding"])
    # The definition digest also includes the live model module schema. Only
    # workers construct that model; they validate the full binding on restore.
    expected = {
        "code_digest": plan["program"]["code_digest"],
        "runtime_digest": digest(plan["runtime_identity"]),
        "dataset_digest": plan["dataset"]["dataset_digest"],
        "assignment_digest": plan["assignment"]["assignment_digest"],
        "schedule_digest": plan["schedule"]["schedule_digest"],
        "world_size": plan["world_size"],
    }
    if any(binding[key] != value for key, value in expected.items()):
        raise TrainingError("Checkpoint source/runtime/data/schedule binding changed")
    if module_schema_digest is not None:
        require_sha(module_schema_digest, "module schema digest")
        definition = digest(
            {"program": plan["program"], "module_schema_digest": module_schema_digest}
        )
        if binding["definition_digest"] != definition:
            raise TrainingError("Checkpoint definition/model schema differs from rank receipt")
    _, transaction = checkpoint.read_transaction(
        checkpoint.Transaction(str(root), reference["transaction_digest"])
    )
    if transaction["binding"] != binding or transaction["progress"] != manifest["progress"]:
        raise TrainingError("Checkpoint transaction/manifest metadata disagree")
    progress = checkpoint.validate_progress(manifest["progress"])
    completed = progress["epoch"] + 1
    if (
        progress["epoch_steps"] != plan["schedule"]["steps_per_epoch"]
        or progress["global_step"] != completed * progress["epoch_steps"]
    ):
        raise TrainingError("Checkpoint epoch/step progress disagrees")
    ranks = manifest["ranks"]
    if type(ranks) is not list or len(ranks) != plan["world_size"]:
        raise TrainingError("Incomplete committed rank metadata")
    for rank, row in enumerate(ranks):
        exact_keys(
            row,
            {"rank", "ready_digest", "replica_digest"},
            name="checkpoint rank acknowledgment",
        )
        integer(row["rank"], "checkpoint rank", rank, rank)
        require_sha(row["ready_digest"])
        require_sha(row["replica_digest"])
    return progress


def _validate_result(result, plan):
    canonical_json(result, limit=MAX_RECEIPT)
    required = {
        "schema_version",
        "kind",
        "status",
        "plan_digest",
        "program_digest",
        "dataset_digest",
        "assignment_digest",
        "schedule_digest",
        "runtime_digest",
        "world_size",
        "completed_epochs",
        "global_step",
        "rank_receipts",
        "latest_checkpoint",
    }
    exact_keys(result, required, name="worker result")
    integer(result["schema_version"], "worker result version", 1, 1)
    if result["kind"] != "ds60-torch-training-worker-result" or result["status"] != "completed":
        raise TrainingError("Worker completion is absent")
    expected = {
        "plan_digest": plan["plan_digest"],
        "program_digest": plan["program"]["program_digest"],
        "dataset_digest": plan["dataset"]["dataset_digest"],
        "assignment_digest": plan["assignment"]["assignment_digest"],
        "schedule_digest": plan["schedule"]["schedule_digest"],
        "runtime_digest": digest(plan["runtime_identity"]),
    }
    if any(result[key] != value for key, value in expected.items()):
        raise TrainingError("Worker result source/plan identity mismatch")
    world, epochs, steps = (
        plan["world_size"],
        plan["schedule"]["epochs"],
        plan["schedule"]["steps_per_epoch"],
    )
    integer(result["world_size"], "result world_size", world, world)
    integer(result["completed_epochs"], "completed_epochs", epochs, epochs)
    integer(result["global_step"], "global_step", epochs * steps, epochs * steps)
    receipts = result["rank_receipts"]
    if type(receipts) is not list or len(receipts) != world:
        raise TrainingError("Incomplete rank receipts")
    latest = _reference(result["latest_checkpoint"])
    if latest is None:
        raise TrainingError("Completed attempt requires a final committed checkpoint")
    files = {row["path"]: row for row in plan["dataset"]["files"]}
    progress = _checkpoint_metadata(plan["resume"], plan) if plan["resume"] is not None else None
    start = progress["epoch"] + 1 if progress is not None else 0
    for rank, receipt in enumerate(receipts):
        required_rank = {
            "rank",
            "world_size",
            "hostname",
            "host_addresses",
            "pid",
            "program_digest",
            "dataset_digest",
            "assignment_digest",
            "schedule_digest",
            "runtime_digest",
            "binding_digest",
            "model_parameter_digest",
            "optimizer_replica_digest",
            "module_schema_digest",
            "start_epoch",
            "completed_epochs",
            "global_step",
            "epoch_ledger",
            "row_deliveries_this_attempt",
            "checkpoint_count",
            "verified_files",
            "latest_checkpoint",
        }
        exact_keys(
            receipt,
            required_rank,
            optional={"execution_policy", "rank_seed", "mode"},
            name="rank receipt",
        )
        integer(receipt["rank"], "logical rank", rank, rank)
        integer(receipt["world_size"], "rank world", world, world)
        integer(receipt["pid"], "rank pid", 1)
        if type(receipt["hostname"]) is not str or not 0 < len(receipt["hostname"]) <= 256:
            raise TrainingError("Invalid rank hostname")
        addresses = receipt["host_addresses"]
        if (
            type(addresses) is not list
            or len(addresses) > 32
            or any(type(value) is not str or not 0 < len(value) <= 128 for value in addresses)
        ):
            raise TrainingError("Invalid rank address list")
        for key in expected.keys() - {"plan_digest"}:
            if receipt[key] != expected[key]:
                raise TrainingError("Rank source/data identity mismatch")
        for key in (
            "binding_digest",
            "model_parameter_digest",
            "optimizer_replica_digest",
            "module_schema_digest",
        ):
            require_sha(receipt[key], key)
        integer(receipt["start_epoch"], "start_epoch", start, start)
        integer(receipt["completed_epochs"], "rank completed_epochs", epochs, epochs)
        integer(receipt["global_step"], "rank global_step", epochs * steps, epochs * steps)
        assigned = plan["assignment"]["ranks"][rank]
        integer(
            receipt["row_deliveries_this_attempt"],
            "delivered rows",
            (epochs - start) * assigned["rows"],
            (epochs - start) * assigned["rows"],
        )
        integer(
            receipt["checkpoint_count"],
            "checkpoint count",
            epochs - start,
            epochs - start,
        )
        verified = [files[name] for name in assigned["files"]]
        if receipt["verified_files"] != verified:
            raise TrainingError("Rank did not verify its exact assigned files")
        ledger = receipt["epoch_ledger"]
        checkpoint.validate_ledger(
            ledger,
            {
                "boundary": "completed_epoch",
                "epoch": epochs - 1,
                "global_step": epochs * steps,
                "epoch_steps": steps,
            },
        )
        if (
            ledger["row_count"] != assigned["rows"]
            or ledger["weight_sum"] != assigned["weight_sum"]
        ):
            raise TrainingError("Rank epoch coverage or normalization differs")
        if len(verified) == 1 and (
            ledger["membership_digest"] != verified[0]["ordered_id_sha256"]
            or ledger["data_digest"] != verified[0]["sha256"]
        ):
            raise TrainingError("Single-file rank consumed different IDs or data")
        if _reference(receipt["latest_checkpoint"]) != latest:
            raise TrainingError("Ranks disagree about the latest checkpoint")
    for key in (
        "binding_digest",
        "model_parameter_digest",
        "optimizer_replica_digest",
        "module_schema_digest",
    ):
        if len({row[key] for row in receipts}) != 1:
            raise TrainingError("Rank replicas or module schema disagree: " + key)
    if plan["resume"] is not None:
        _checkpoint_metadata(
            plan["resume"],
            plan,
            module_schema_digest=receipts[0]["module_schema_digest"],
        )
    root = _owned_path(latest["path"])
    if _owned_path(plan["checkpoint_root"]) not in root.parents:
        raise TrainingError("Final checkpoint is not in this attempt's owned root")
    final = _checkpoint_metadata(
        latest, plan, module_schema_digest=receipts[0]["module_schema_digest"]
    )
    if final["epoch"] + 1 != epochs or final["global_step"] != epochs * steps:
        raise TrainingError("Latest checkpoint does not attest final epoch state")
    return result


def _verify_final_state(plan: dict, result: dict) -> None:
    """Read every bounded committed rank payload before publishing success."""
    reference = _reference(result["latest_checkpoint"])
    if reference is None:
        raise TrainingError("Final committed checkpoint is absent")
    root = _owned_path(reference["path"])
    manifest = checkpoint.read_json(root / "manifest.json", allow_links=True)
    binding = checkpoint.validate_binding(manifest["binding"])
    receipts = result["rank_receipts"]
    for rank, receipt in enumerate(receipts):
        loaded = checkpoint.load_rank(
            root,
            expected_binding=binding,
            expected_manifest_digest=reference["manifest_digest"],
            rank=rank,
        )
        members = []
        for item in loaded.binding["model_layout"]:
            if item["role"] != "parameter":
                continue
            tensor = loaded.state["model"][item["name"]]
            members.append(
                {
                    "name": item["name"],
                    "dtype": tensor.dtype,
                    "shape": list(tensor.shape),
                    "data_sha256": checkpoint.sha(tensor.data),
                }
            )
        expected = {
            "binding_digest": checkpoint.digest_value(loaded.binding),
            "model_parameter_digest": checkpoint.digest_value(members),
            "optimizer_replica_digest": checkpoint.replica_digest(loaded.state, loaded.binding),
        }
        if any(receipt[name] != value for name, value in expected.items()):
            raise TrainingError("Committed rank payload differs from worker receipt")
        if loaded.ledger != receipt["epoch_ledger"]:
            raise TrainingError("Committed rank ledger differs from worker receipt")


def _error(error: Exception) -> dict:
    return {"type": type(error).__name__, "message": str(error)[:2048]}


def _publish(root: Path, name: str, value, limit=MAX_RECEIPT):
    temporary = root / ("." + name + ".pending")
    write_new_json(temporary, value, limit=limit)
    os.link(temporary, root / name, follow_symlinks=False)
    temporary.unlink()
    descriptor = os.open(root, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def run_training(
    spark,
    program: TrainingProgram,
    manifest_path: Path | str,
    *,
    mode: str,
    world_size: int,
    assignment: dict | None = None,
    epochs: int = 1,
    steps_per_epoch: int = 1,
    max_batch_rows: int = 32768,
    seed: int = 0,
    output_dir: Path | str,
    observer,
    timeout_seconds: float = 180,
    resume=None,
) -> dict:
    """Launch one explicit CPU attempt; success requires independent task proof.

    The cancellation watchdog targets only this job group. The external owned
    integration controller retains the hard process/container deadline.
    """
    context = _spark_admission(spark, mode, world_size)
    if not isinstance(program, TrainingProgram):
        raise TrainingError("Use an explicitly source-bound TrainingProgram")
    if not callable(getattr(observer, "before", None)) or not callable(
        getattr(observer, "after", None)
    ):
        raise TrainingError("An independent before/after executor observer is required")
    timeout = finite(timeout_seconds, "timeout_seconds", minimum=0.01, maximum=600)
    descriptor = program.descriptor()
    path = _owned_path(manifest_path)
    dataset = data.load_manifest(path)
    if descriptor["feature_names"] != dataset["feature_names"] or (
        descriptor["target_domain"] == "class_index"
    ) != (dataset["label_kind"] == "class_index"):
        raise TrainingError("Program features or target domain differ from the snapshot")
    assignment = (
        data.assign_shards(dataset, world_size)
        if assignment is None
        else data._assignment(assignment, dataset)
    )
    if assignment["world_size"] != world_size:
        raise TrainingError("Assignment world differs from requested mode")
    requested_schedule = schedule(
        assignment,
        epochs=epochs,
        steps_per_epoch=steps_per_epoch,
        max_batch_rows=max_batch_rows,
        seed=seed,
    )
    runtime = _runtime_identity()
    if type(runtime) is not dict or not runtime:
        raise TrainingError("Missing prepared runtime identity")
    canonical_json(runtime, limit=262144)
    wrapper = _require_prepared_wrapper()
    if wrapper.get("status") != "prepared":
        raise TrainingError("Spark wrapper requires explicit prior preparation")
    output = _owned_path(output_dir)
    if not output.parent.is_dir() or output.exists():
        raise TrainingError("Choose a fresh owned output directory with an existing parent")
    run_id = uuid.uuid4().hex
    plan = {
        "schema_version": 1,
        "kind": "ds60-torch-training-plan",
        "run_id": run_id,
        "mode": mode,
        "world_size": world_size,
        "program": descriptor,
        "manifest_path": str(path),
        "dataset": dataset,
        "assignment": assignment,
        "schedule": requested_schedule,
        "output_dir": str(output),
        "checkpoint_root": str(output / "checkpoints"),
        "resume": _reference(resume),
        "runtime_identity": runtime,
        "timeout_seconds": timeout,
    }
    if plan["resume"] is not None:
        progress = _checkpoint_metadata(plan["resume"], plan)
        if progress["epoch"] + 1 >= epochs:
            raise TrainingError("Resume is already at or after the requested target epoch")
    plan["plan_digest"] = digest(plan)
    output.mkdir(mode=0o700)
    (output / "checkpoints").mkdir(mode=0o700)
    _publish(output, "plan.json", plan, limit=1_000_000)
    previous = {name: context.getLocalProperty(name) for name in GROUP_PROPERTIES}
    done, timed_out = threading.Event(), threading.Event()
    cancellation_errors = []

    def cancel():
        if done.is_set():
            return
        timed_out.set()
        try:
            context.cancelJobGroup(run_id)
        except Exception as error:  # noqa: BLE001 - retain cancellation failure
            cancellation_errors.append(_error(error))

    timer = threading.Timer(timeout, cancel)
    timer.daemon = True
    began = time.monotonic()
    failure = None
    token = result = observation = proof = None
    after_attempted = False
    try:
        context.setJobGroup(run_id, "DS60 bounded CPU training " + run_id, interruptOnCancel=True)
        timer.start()
        token = observer.before(spark, plan)
        canonical_json(token, limit=MAX_OBSERVATION_BYTES)
        result = _distributor_class()(
            num_processes=world_size, local_mode=False, use_gpu=False
        ).run(_worker(), plan)
        _validate_result(result, plan)
        if timed_out.is_set() or time.monotonic() - began > timeout:
            raise TrainingError("Owned training attempt exceeded its deadline")
        after_attempted = True
        observation = observer.after(spark, plan, token, result, error=None)
        proof = validate_evidence(plan, result, observation)
        _verify_final_state(plan, result)
        if timed_out.is_set() or time.monotonic() - began > timeout:
            raise TrainingError("Owned observation exceeded its deadline")
    except Exception as error:  # noqa: BLE001 - publish a failed attempt receipt
        failure = error
        if token is not None and not after_attempted:
            after_attempted = True
            try:
                observation = observer.after(spark, plan, token, result, error=_error(error))
            except Exception as capture_error:  # noqa: BLE001 - preserve primary failure
                cancellation_errors.append({"observation_error": _error(capture_error)})
        try:
            context.cancelJobGroup(run_id)
        except Exception as cancel_error:  # noqa: BLE001 - preserve primary failure
            cancellation_errors.append(_error(cancel_error))
    finally:
        done.set()
        timer.cancel()
        if timer.ident is not None:
            timer.join(timeout=0.1)
        for name, value in previous.items():
            try:
                context.setLocalProperty(name, value)
            except Exception as restore_error:  # noqa: BLE001 - record property restoration failure
                cancellation_errors.append({"property_restore_error": _error(restore_error)})
                if failure is None:
                    failure = restore_error
    if observation is not None:
        try:
            _publish(output, "observation.json", observation, limit=MAX_OBSERVATION_BYTES)
        except Exception as evidence_error:  # noqa: BLE001 - record evidence publication failure
            if failure is None:
                failure = evidence_error
            else:
                cancellation_errors.append({"evidence_write_error": _error(evidence_error)})
    if failure is not None:
        receipt = {
            "schema_version": 1,
            "kind": "ds60-torch-training-attempt",
            "run_id": run_id,
            "plan_digest": plan["plan_digest"],
            "status": "failed",
            "error": _error(failure),
            "timed_out": timed_out.is_set(),
            "cleanup_errors": cancellation_errors,
            "checkpoint_files_do_not_imply_success": True,
        }
        _publish(output, "result.json", receipt)
        raise failure
    receipt = {
        "schema_version": 1,
        "kind": "ds60-torch-training-attempt",
        "run_id": run_id,
        "plan_digest": plan["plan_digest"],
        "status": "completed",
        "worker_result": result,
        "executor_evidence": proof,
    }
    try:
        canonical_json(receipt, limit=MAX_RECEIPT)
    except Exception as size_error:
        failed = {
            "schema_version": 1,
            "kind": "ds60-torch-training-attempt",
            "run_id": run_id,
            "plan_digest": plan["plan_digest"],
            "status": "failed",
            "error": _error(size_error),
            "timed_out": timed_out.is_set(),
            "cleanup_errors": cancellation_errors,
            "checkpoint_files_do_not_imply_success": True,
        }
        _publish(output, "result.json", failed)
        raise
    _publish(output, "result.json", receipt)
    return receipt
