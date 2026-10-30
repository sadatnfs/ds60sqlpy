"""Pure launch and listener admission checks with no Spark or Torch runtime."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from ds60_torch_training import launch, observer
from ds60_torch_training.contracts import TrainingError, digest


@pytest.fixture(autouse=True)
def committed_metadata_double(monkeypatch):
    monkeypatch.setattr(
        launch,
        "_checkpoint_metadata",
        lambda *args, **kwargs: {"epoch": 0, "global_step": 1, "epoch_steps": 1},
    )


class Conf:
    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        return self.values.get(key, default)

    def getAll(self):
        return list(self.values.items())


def context(**updates):
    values = {
        "spark.task.maxFailures": "1",
        "spark.executor.cores": "1",
        "spark.task.cpus": "1",
        "spark.speculation": "false",
        "spark.dynamicAllocation.enabled": "false",
    } | updates
    sc = SimpleNamespace(_jsc=object(), master="spark://master:7077", version="4.0.1")
    sc.getConf = lambda: Conf(values)
    return SimpleNamespace(_jsparkSession=object(), sparkContext=sc, version="4.0.1")


def test_spark_admission_requires_executor_cpu_and_single_attempt():
    spark = context()
    assert launch._spark_admission(spark, "executor_single", 1) is spark.sparkContext
    assert launch._spark_admission(spark, "executor_ddp", 2) is spark.sparkContext
    for mode, world in [("executor_single", 2), ("executor_ddp", 1), ("driver", 1)]:
        with pytest.raises(TrainingError):
            launch._spark_admission(spark, mode, world)
    for setting in [
        {"spark.task.maxFailures": "4"},
        {"spark.speculation": "true"},
        {"spark.executor.resource.gpu.amount": "1"},
    ]:
        with pytest.raises(TrainingError):
            launch._spark_admission(context(**setting), "executor_single", 1)
    spark.sparkContext.master = "local[2]"
    with pytest.raises(TrainingError, match="local masters"):
        launch._spark_admission(spark, "executor_single", 1)


def plan_and_result(world=1):
    sha = "a" * 64
    probe = "b" * 64
    program = {"program_digest": sha, "code_digest": probe}
    dataset = {
        "dataset_digest": sha,
        "files": [
            {
                "path": f"shards/part-{rank:05d}.jsonl",
                "rows": 1,
                "weight_sum": 1.0,
                "ordered_id_sha256": sha,
                "sha256": probe,
            }
            for rank in range(world)
        ],
    }
    assignment = {
        "assignment_digest": probe,
        "ranks": [
            {"files": [row["path"]], "rows": 1, "weight_sum": 1.0} for row in dataset["files"]
        ],
    }
    schedule = {"schedule_digest": sha, "epochs": 1, "steps_per_epoch": 1}
    plan = {
        "plan_digest": sha,
        "program": program,
        "dataset": dataset,
        "assignment": assignment,
        "schedule": schedule,
        "runtime_identity": {"x": 1},
        "world_size": world,
        "resume": None,
        "checkpoint_root": "/private/tmp/checkpoints",
    }
    latest = {
        "path": "/private/tmp/checkpoints/epoch-0000",
        "manifest_digest": sha,
        "transaction_digest": probe,
        "training_run_status": "not_attested",
    }
    receipts = []
    for rank, file in enumerate(dataset["files"]):
        receipts.append(
            {
                "rank": rank,
                "world_size": world,
                "hostname": f"worker{rank}",
                "host_addresses": [],
                "pid": rank + 100,
                "program_digest": sha,
                "dataset_digest": sha,
                "assignment_digest": probe,
                "schedule_digest": sha,
                "runtime_digest": digest(plan["runtime_identity"]),
                "binding_digest": sha,
                "model_parameter_digest": sha,
                "optimizer_replica_digest": sha,
                "module_schema_digest": sha,
                "start_epoch": 0,
                "completed_epochs": 1,
                "global_step": 1,
                "epoch_ledger": {
                    "row_count": 1,
                    "weight_sum": 1.0,
                    "membership_digest": sha,
                    "data_digest": probe,
                    "steps": 1,
                },
                "row_deliveries_this_attempt": 1,
                "checkpoint_count": 1,
                "verified_files": [file],
                "latest_checkpoint": latest,
            }
        )
    result = {
        "schema_version": 1,
        "kind": "ds60-torch-training-worker-result",
        "status": "completed",
        "plan_digest": sha,
        "program_digest": sha,
        "dataset_digest": sha,
        "assignment_digest": probe,
        "schedule_digest": sha,
        "runtime_digest": digest(plan["runtime_identity"]),
        "world_size": world,
        "completed_epochs": 1,
        "global_step": 1,
        "rank_receipts": receipts,
        "latest_checkpoint": latest,
    }
    return plan, result


def test_worker_result_exact_coverage_and_identity():
    plan, result = plan_and_result(2)
    assert launch._validate_result(result, plan) is result
    result["rank_receipts"][1]["verified_files"] = []
    with pytest.raises(TrainingError, match="exact assigned files"):
        launch._validate_result(result, plan)


def test_worker_result_refuses_unbounded_and_changed_source():
    plan, result = plan_and_result()
    result["rank_receipts"][0]["hostname"] = "x" * 100_000
    with pytest.raises(TrainingError):
        launch._validate_result(result, plan)
    plan, result = plan_and_result()
    result["program_digest"] = "0" * 64
    with pytest.raises(TrainingError, match="identity mismatch"):
        launch._validate_result(result, plan)


def test_completed_attempt_needs_committed_epoch_checkpoint():
    plan, result = plan_and_result()
    result["latest_checkpoint"] = None
    with pytest.raises(TrainingError, match="final committed checkpoint"):
        launch._validate_result(result, plan)
    plan, result = plan_and_result()
    result["rank_receipts"][0]["checkpoint_count"] = 0
    with pytest.raises(TrainingError, match="checkpoint count"):
        launch._validate_result(result, plan)


def test_final_payload_is_loaded_for_every_rank_and_matches_receipts(monkeypatch):
    plan, result = plan_and_result(2)
    binding = {"model_layout": [{"name": "0.weight", "role": "parameter"}]}
    tensor = SimpleNamespace(dtype="float64", shape=(1, 1), data=b"12345678")
    ledger = result["rank_receipts"][0]["epoch_ledger"]
    loaded = SimpleNamespace(binding=binding, state={"model": {"0.weight": tensor}}, ledger=ledger)
    visited = []
    monkeypatch.setattr(
        launch.checkpoint, "read_json", lambda *args, **kwargs: {"binding": binding}
    )
    monkeypatch.setattr(launch.checkpoint, "validate_binding", lambda value: value)
    monkeypatch.setattr(
        launch.checkpoint, "load_rank", lambda *args, rank, **kwargs: visited.append(rank) or loaded
    )
    monkeypatch.setattr(launch.checkpoint, "replica_digest", lambda *args: "b" * 64)
    members = [
        {
            "name": "0.weight",
            "dtype": "float64",
            "shape": [1, 1],
            "data_sha256": launch.checkpoint.sha(tensor.data),
        }
    ]
    for receipt in result["rank_receipts"]:
        receipt["binding_digest"] = launch.checkpoint.digest_value(binding)
        receipt["model_parameter_digest"] = launch.checkpoint.digest_value(members)
        receipt["optimizer_replica_digest"] = "b" * 64
    launch._verify_final_state(plan, result)
    assert visited == [0, 1]
    result["rank_receipts"][1]["model_parameter_digest"] = "0" * 64
    with pytest.raises(TrainingError, match="payload differs"):
        launch._verify_final_state(plan, result)


def event(kind, rank=0, executor="0", *, successful=True, task_id=17):
    row = {
        "kind": kind,
        "stage_id": 5,
        "stage_attempt": 0,
        "partition_id": rank,
        "task_id": task_id,
        "attempt": 0,
        "executor_id": executor,
        "host": f"worker{rank}",
    }
    if kind == "task_end":
        row["successful"] = successful
    return row


def observation(plan, events):
    sha = "a" * 64
    return {
        "schema_version": 1,
        "kind": "ds60-torch-executor-observation",
        "run_id": plan["run_id"],
        "probe_identity": {
            "source_sha256": sha,
            "jar_sha256": sha,
            "loaded_jar_sha256": sha,
            "metadata_sha256": sha,
        },
        "before_identities": [],
        "after_identities": [],
        "excluded_stage_ids": [],
        "events": events,
    }


def test_single_executor_observer_uses_listener_without_two_task_probe():
    plan, result = plan_and_result()
    plan["run_id"] = "run"
    proof = observer.validate_evidence(
        plan, result, observation(plan, [event("task_start"), event("task_end")])
    )
    assert proof["matched_ranks"][0]["executor_id"] == "0"
    assert proof["matched_ranks"][0]["jvm_pid"] is None


@pytest.mark.parametrize(
    "events",
    [
        [event("task_start"), event("task_end", successful=False)],
        [event("task_start"), event("task_end"), event("task_end", task_id=18)],
        [event("task_start"), event("task_end", executor="driver")],
        [event("task_start"), event("task_end"), {"kind": "executor_removed"}],
    ],
)
def test_observer_refuses_failure_retry_driver_and_removal(events):
    plan, result = plan_and_result()
    plan["run_id"] = "run"
    with pytest.raises(TrainingError):
        observer.validate_evidence(plan, result, observation(plan, events))


def test_two_rank_observer_requires_stable_independent_executors():
    plan, result = plan_and_result(2)
    plan["run_id"] = "run"
    records = observation(
        plan,
        [
            event("task_start", 0, "0", task_id=17),
            event("task_start", 1, "1", task_id=18),
            event("task_end", 0, "0", task_id=17),
            event("task_end", 1, "1", task_id=18),
        ],
    )
    identities = [
        {
            "kind": "executor_identity",
            "executor_id": str(rank),
            "pid": rank + 200,
            "stage_id": stage,
            "partition_id": rank,
            "attempt": 0,
            "stage_attempt": 0,
            "host": f"worker{rank}",
        }
        for rank in range(2)
        for stage in [3]
    ]
    records["before_identities"] = identities
    records["after_identities"] = [{**row, "stage_id": 7} for row in identities]
    records["excluded_stage_ids"] = [3, 7]
    assert len(observer.validate_evidence(plan, result, records)["matched_ranks"]) == 2
    records["after_identities"][1]["pid"] = 999
    with pytest.raises(TrainingError, match="changed"):
        observer.validate_evidence(plan, result, records)


def test_public_run_route_preserves_failure_receipt_and_context(tmp_path, monkeypatch):
    spark = context()
    properties = {name: f"prior-{i}" for i, name in enumerate(launch.GROUP_PROPERTIES)}
    groups = []
    cancellations = []
    spark.sparkContext.getLocalProperty = lambda key: properties[key]
    spark.sparkContext.setLocalProperty = lambda key, value: properties.__setitem__(key, value)
    spark.sparkContext.setJobGroup = lambda *args, **kwargs: groups.append((args, kwargs))
    spark.sparkContext.cancelJobGroup = cancellations.append

    class Program:
        def descriptor(self):
            return {
                "feature_names": ["x"],
                "target_domain": "real",
                "program_digest": "a" * 64,
            }

    class Distributor:
        def __init__(self, **kwargs):
            assert kwargs == {"num_processes": 1, "local_mode": False, "use_gpu": False}

        def run(self, worker, plan):
            assert plan["mode"] == "executor_single"
            raise RuntimeError("controlled worker failure")

    class Observer:
        def before(self, spark, plan):
            return {"token": plan["run_id"]}

        def after(self, spark, plan, token, result, *, error=None):
            assert error["type"] == "RuntimeError"
            return {"failed_run": plan["run_id"]}

    monkeypatch.setattr(launch, "TrainingProgram", Program)
    monkeypatch.setattr(
        launch.data,
        "load_manifest",
        lambda _: {
            "feature_names": ["x"],
            "label_kind": "float",
            "dataset_digest": "a" * 64,
        },
    )
    monkeypatch.setattr(launch.data, "assign_shards", lambda *_: {"world_size": 1})
    monkeypatch.setattr(launch, "schedule", lambda *args, **kwargs: {"steps_per_epoch": 1})
    monkeypatch.setattr(launch, "_runtime_identity", lambda: {"runtime": "checked"})
    monkeypatch.setattr(launch, "_require_prepared_wrapper", lambda: {"status": "prepared"})
    monkeypatch.setattr(launch, "_distributor_class", lambda: Distributor)
    monkeypatch.setattr(launch, "_worker", lambda: object())
    output = tmp_path / "attempt"
    with pytest.raises(RuntimeError, match="controlled worker failure"):
        launch.run_training(
            spark,
            Program(),
            tmp_path / "manifest.json",
            mode="executor_single",
            world_size=1,
            output_dir=output,
            observer=Observer(),
        )
    assert len(groups) == 1 and len(cancellations) == 1
    assert properties == {name: f"prior-{i}" for i, name in enumerate(launch.GROUP_PROPERTIES)}
    assert json.loads((output / "result.json").read_text())["status"] == "failed"
    assert json.loads((output / "observation.json").read_text())["failed_run"]


def test_oversized_success_receipt_publishes_failure(tmp_path, monkeypatch):
    spark = context()
    spark.sparkContext.getLocalProperty = lambda _: None
    spark.sparkContext.setLocalProperty = lambda *_: None
    spark.sparkContext.setJobGroup = lambda *args, **kwargs: None
    spark.sparkContext.cancelJobGroup = lambda _: None

    class Program:
        def descriptor(self):
            return {"feature_names": ["x"], "target_domain": "real"}

    class Distributor:
        def __init__(self, **kwargs):
            assert kwargs["local_mode"] is False

        def run(self, worker, plan):
            return {"worker": "bounded"}

    class Observer:
        def before(self, spark, plan):
            return {"token": 1}

        def after(self, spark, plan, token, result, *, error=None):
            return {"events": []}

    monkeypatch.setattr(launch, "TrainingProgram", Program)
    monkeypatch.setattr(
        launch.data,
        "load_manifest",
        lambda _: {"feature_names": ["x"], "label_kind": "float"},
    )
    monkeypatch.setattr(launch.data, "assign_shards", lambda *_: {"world_size": 1})
    monkeypatch.setattr(launch, "schedule", lambda *args, **kwargs: {"steps_per_epoch": 1})
    monkeypatch.setattr(launch, "_runtime_identity", lambda: {"runtime": "checked"})
    monkeypatch.setattr(launch, "_require_prepared_wrapper", lambda: {"status": "prepared"})
    monkeypatch.setattr(launch, "_distributor_class", lambda: Distributor)
    monkeypatch.setattr(launch, "_worker", lambda: object())
    monkeypatch.setattr(launch, "_validate_result", lambda result, plan: result)
    monkeypatch.setattr(launch, "validate_evidence", lambda plan, result, raw: {"proof": True})
    monkeypatch.setattr(launch, "_verify_final_state", lambda plan, result: None)
    original = launch.canonical_json

    def refuse_success(value, *, limit=None):
        if (
            isinstance(value, dict)
            and value.get("status") == "completed"
            and value.get("kind") == "ds60-torch-training-attempt"
        ):
            raise TrainingError("final receipt exceeds bound")
        return original(value, limit=limit)

    monkeypatch.setattr(launch, "canonical_json", refuse_success)
    output = tmp_path / "oversized"
    with pytest.raises(TrainingError, match="final receipt exceeds bound"):
        launch.run_training(
            spark,
            Program(),
            tmp_path / "manifest.json",
            mode="executor_single",
            world_size=1,
            output_dir=output,
            observer=Observer(),
        )
    assert json.loads((output / "result.json").read_text())["status"] == "failed"
    assert json.loads((output / "observation.json").read_text()) == {"events": []}
