# SPDX-License-Identifier: Apache-2.0
"""Bounded CPU executor function for the public TorchDistributor.run path.

Importing this module does not load Spark or Torch. Training runs only inside a
TorchDistributor executor process with an explicit, fixed logical rank.
"""

from __future__ import annotations

import atexit
import contextlib
import faulthandler
import importlib.util
import json
import os
import platform
import random
import signal
import socket
import sys
import time
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path
from typing import Any

from . import checkpoint, data, torch_adapter
from .contracts import (
    MAX_RECEIPT,
    TrainingError,
    canonical_json,
    digest,
    exact_keys,
    integer,
    sha256_bytes,
)
from .program import TrainingProgram, ledger
from .program import schedule as make_schedule

REVIEWED_DISTRIBUTORS = {
    "4.0.1": "fa54028c2ec3489702a172ade895fac9c53e58db45e08d7bf34b8e7d67737ba3",
    "4.3.0": "4136a0ac4fdfe26907e7841b45e0c63ee8104623102434679d7e023668e0b8a9",
}
PINNED_SOURCES = {
    "torch.nn.parallel.distributed": (
        "ff36d22a7d8d76713c99b37393e6cb9876de01043a3d7255527e58a6bb89f30f"
    ),
    "torch.optim.optimizer": "4b0ecf48fa034f60e6ac1e5055846bbc907ec63c2f174b1bb81472354593075b",
    "torch.random": "0b2bd65c8fdf324e00ed2c64e7b06ca5d5ff96053001055c86352c0b3668d0be",
}
RUNTIME_MODULES = (
    "ds60_torch_training.contracts",
    "ds60_torch_training.program",
    "ds60_torch_training.data",
    "ds60_torch_training.checkpoint",
    "ds60_torch_training.torch_adapter",
    "ds60_torch_training.runner",
    "ds60_torch_training.launch",
    "ds60_torch_training.observer",
    "ds60_spark_likelihood.registry",
    "ds60_spark_likelihood.integrations.prepare_spark",
    "pyspark.ml.torch.distributor",
    "torch.nn.parallel.distributed",
    "torch.optim.optimizer",
    "torch.random",
)


def _source_digest(module_name: str) -> str:
    spec = importlib.util.find_spec(module_name)
    if (
        spec is None
        or spec.origin is None
        or not spec.origin.endswith(".py")
        or spec.loader is None
    ):
        raise TrainingError(
            "Required runtime module has no inspectable Python source: " + module_name
        )
    if not hasattr(spec.loader, "get_data"):
        raise TrainingError("Required runtime source loader cannot read bytes: " + module_name)
    raw = spec.loader.get_data(spec.origin)
    if len(raw) > 4 * 1024 * 1024:
        raise TrainingError("Required runtime source exceeds bound: " + module_name)
    return sha256_bytes(raw)


def runtime_identity() -> dict:
    """Identify shared code and software without rank-specific environment data."""
    import ds60_spark_likelihood
    import numpy
    import pyspark
    import torch
    from ds60_spark_likelihood.integrations.prepare_spark import (
        require_prepared_wrapper,
    )

    if sys.byteorder != "little" or platform.machine().lower() not in {
        "aarch64",
        "arm64",
        "x86_64",
        "amd64",
    }:
        raise TrainingError("Only little-endian native CPU architecture is supported")
    spark_version = str(pyspark.__version__)
    if (
        not str(torch.__version__).startswith("2.15.0+cpu")
        or spark_version not in REVIEWED_DISTRIBUTORS
    ):
        raise TrainingError("Expected prepared Torch 2.15.0+cpu and reviewed Spark 4.0.1 or 4.3.0")
    wrapper = require_prepared_wrapper()
    if wrapper["status"] != "prepared" or wrapper.get("spark_version") != spark_version:
        raise TrainingError("Prepared Spark torchrun wrapper is required")
    sources = {name: _source_digest(name) for name in RUNTIME_MODULES}
    pinned = dict(PINNED_SOURCES)
    pinned["pyspark.ml.torch.distributor"] = REVIEWED_DISTRIBUTORS[spark_version]
    if any(sources[name] != expected for name, expected in pinned.items()):
        raise TrainingError("Installed Spark or Torch source differs from reviewed CPU runtime")
    result = {
        "kind": "ds60-torch-cpu-runtime-v1",
        "python_minor": list(sys.version_info[:2]),
        "architecture": platform.machine().lower(),
        "byteorder": sys.byteorder,
        "spark_version": str(pyspark.__version__),
        "torch_version": str(torch.__version__),
        "numpy_version": str(numpy.__version__),
        "package_version": str(ds60_spark_likelihood.__version__),
        "wrapper": wrapper,
        "sources": sources,
    }
    canonical_json(result, limit=262144)
    return result


def _admit_runtime_identity(expected: dict) -> None:
    if runtime_identity() != expected:
        raise TrainingError("Executor software/source identity differs from driver")


def _rank_environment(world: int) -> int:
    values = {}
    for name in ("RANK", "WORLD_SIZE", "LOCAL_RANK"):
        raw = os.environ.get(name)
        if raw is None or not raw.isdecimal():
            raise TrainingError("TorchDistributor did not set an exact " + name)
        values[name] = int(raw)
    integer(values["WORLD_SIZE"], "actual world size", world, world)
    integer(values["RANK"], "logical rank", 0, world - 1)
    integer(values["LOCAL_RANK"], "local rank", 0, world - 1)
    if os.environ.get("CUDA_VISIBLE_DEVICES", "") != "":
        raise TrainingError("CPU mode refuses visible CUDA devices")
    return values["RANK"]


def _construct(program: TrainingProgram, descriptor: dict, torch):
    config = descriptor["configuration"] or {}
    exact_keys(config, {"model", "loss", "optimizer"}, name="training factory configuration")
    if any(type(config[key]) is not dict for key in ("model", "loss", "optimizer")):
        raise TrainingError("Each training factory requires a JSON object configuration")
    model = program.model_factory(config["model"])
    loss = program.loss_factory(config["loss"])
    if not isinstance(model, torch.nn.Module) or not isinstance(loss, torch.nn.Module):
        raise TrainingError("Factories must construct ordinary Torch modules")
    if any(value.device.type != "cpu" for value in model.parameters()):
        raise TrainingError("Model factory must construct CPU parameters")
    if any(True for _ in model.buffers()):
        raise TrainingError("Mutable model buffers need a separate synchronization policy")
    dtype = torch.float32 if descriptor["precision"] == "float32" else torch.float64
    if any(value.dtype != dtype for value in model.parameters()):
        raise TrainingError("Model factory parameter dtype differs from declared precision")
    if getattr(loss, "reduction", None) != "none":
        raise TrainingError("Loss factory must use reduction=none")
    allowed = {
        "binary": {torch.nn.BCEWithLogitsLoss},
        "real": {
            torch.nn.MSELoss,
            torch.nn.L1Loss,
            torch.nn.SmoothL1Loss,
            torch.nn.HuberLoss,
        },
        "class_index": {torch.nn.CrossEntropyLoss, torch.nn.NLLLoss},
    }
    if type(loss) not in allowed[descriptor["target_domain"]]:
        raise TrainingError("Loss class does not match target domain")
    if any(value is not None for value in loss._buffers.values()):
        raise TrainingError("Class or positive weighting inside the loss is unsupported")
    if type(loss) in {torch.nn.CrossEntropyLoss, torch.nn.NLLLoss} and loss.ignore_index >= 0:
        raise TrainingError("Ignoring declared class labels is unsupported")
    if type(loss) is torch.nn.CrossEntropyLoss and loss.label_smoothing != 0:
        raise TrainingError("Class label smoothing needs a separate target contract")
    optimizer = program.optimizer_factory(model.parameters(), config["optimizer"])
    if not isinstance(optimizer, torch.optim.Optimizer):
        raise TrainingError("Optimizer factory returned an unsupported object")
    return model, loss, optimizer, dtype


def _batch_loss(model, loss, rows: list[dict], domain: str, dtype, torch):
    x = torch.tensor([row["features"] for row in rows], dtype=dtype, device="cpu")
    labels = [row["label"] for row in rows]
    if domain == "binary" and any(label not in (0, 1, 0.0, 1.0) for label in labels):
        raise TrainingError("Binary targets must be exactly zero or one")
    if domain == "class_index":
        y = torch.tensor(labels, dtype=torch.int64, device="cpu")
    else:
        y = torch.tensor(labels, dtype=dtype, device="cpu")
    output = model(x)
    if not isinstance(output, torch.Tensor) or output.device.type != "cpu" or output.dtype != dtype:
        raise TrainingError("Model output must be a dense CPU tensor of declared precision")
    if domain == "class_index":
        if output.ndim != 2 or output.shape[0] != len(rows) or output.shape[1] < 2:
            raise TrainingError("Class model must return [batch, classes]")
        if any(label >= output.shape[1] for label in labels):
            raise TrainingError("Class target exceeds model output")
    else:
        if tuple(output.shape) not in {(len(rows),), (len(rows), 1)}:
            raise TrainingError("Scalar target model must return [batch] or [batch, 1]")
        if output.ndim == 2:
            y = y.reshape(-1, 1)
    values = loss(output, y)
    if not isinstance(values, torch.Tensor) or values.numel() != len(rows):
        raise TrainingError("Loss must return exactly one value per observation")
    values = values.reshape(len(rows))
    if not torch.isfinite(values).all().item():
        raise TrainingError("Nonfinite per-observation loss")
    weights = torch.tensor([row["weight"] for row in rows], dtype=dtype, device="cpu")
    return (values * weights).sum(), weights.sum()


def _all_gather(dist, value: Any, world: int) -> list[Any]:
    gathered: list[Any] = [None] * world
    dist.all_gather_object(gathered, value)
    return gathered


def _broadcast(dist, value: Any, rank: int) -> Any:
    box = [value if rank == 0 else None]
    dist.broadcast_object_list(box, src=0)
    return box[0]


def _addresses(host: str) -> list[str]:
    values = sorted({item[4][0] for item in socket.getaddrinfo(host, None, family=socket.AF_INET)})
    if not values or len(values) > 32:
        raise TrainingError("Executor needs bounded resolved IPv4 host addresses")
    return values


def _tensor_digest(model, adapter=torch_adapter) -> str:
    members = []
    for name, value in model.named_parameters():
        item = adapter.tensor_data(value)
        members.append(
            {
                "name": name,
                "dtype": item.dtype,
                "shape": list(item.shape),
                "data_sha256": checkpoint.sha(item.data),
            }
        )
    return checkpoint.digest_value(members)


DIAGNOSTICS_DIRECTORY = "diagnostics"
EXIT_GRACE_SECONDS = 15.0
MIN_STACK_INTERVAL_SECONDS = 5.0
MAX_STEP_RECORDS = 256
# faulthandler writes to these descriptors until process exit, so they stay open.
_RETAINED_STREAMS: list = []


def _open_new_text(path: Path):
    descriptor = os.open(
        checkpoint.safe_path(path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    return os.fdopen(descriptor, "w", encoding="utf-8", buffering=1)


def _thread_count() -> int | None:
    try:
        return sum(1 for _ in Path("/proc/self/task").iterdir())
    except OSError:
        return None


class _RankDiagnostics:
    """Best-effort rank progress and stack evidence beside the shared checkpoints.

    Training never reads these files, and a failed diagnostics write only disables
    later records. faulthandler writes every thread's Python stack periodically
    before the driver deadline, on SIGTERM, and when the process outlives the rank
    function by EXIT_GRACE_SECONDS, so a stalled rank leaves its location behind.
    """

    def __init__(self, progress=None, stacks=None):
        self._progress = progress
        self._stacks = stacks
        self._began = time.monotonic()
        self._steps = 0

    @classmethod
    def start(cls, plan: dict, rank: int) -> _RankDiagnostics:
        try:
            root = checkpoint.safe_path(Path(plan["output_dir"]) / DIAGNOSTICS_DIRECTORY)
            root.mkdir(mode=0o700, exist_ok=True)
            stem = f"rank-{rank:05d}-pid-{os.getpid()}"
            progress = _open_new_text(root / (stem + ".progress.jsonl"))
            stacks = _open_new_text(root / (stem + ".stacks.txt"))
        except Exception:  # noqa: BLE001 - evidence must never change the training outcome
            return cls()
        _RETAINED_STREAMS.extend((progress, stacks))
        diagnostics = cls(progress, stacks)
        interval = max(MIN_STACK_INTERVAL_SECONDS, 0.3 * float(plan["timeout_seconds"]))
        try:
            faulthandler.dump_traceback_later(interval, repeat=True, file=stacks)
            if hasattr(faulthandler, "register"):
                faulthandler.register(signal.SIGTERM, file=stacks, all_threads=True, chain=True)
            atexit.register(diagnostics.record, "interpreter_exit")
        except Exception:  # noqa: BLE001 - progress records remain useful without stacks
            pass
        diagnostics.record(
            "start",
            rank=rank,
            pid=os.getpid(),
            hostname=socket.gethostname(),
            run_id=plan["run_id"],
            stack_interval_seconds=interval,
            cpu_count=os.cpu_count(),
            affinity=len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            omp_num_threads=os.environ.get("OMP_NUM_THREADS"),
            threads=_thread_count(),
        )
        return diagnostics

    def record(self, event: str, **fields: Any) -> None:
        if self._progress is None:
            return
        try:
            entry = {
                "event": event,
                "seconds": round(time.monotonic() - self._began, 3),
                "unix_time": round(time.time(), 3),
                **fields,
            }
            self._progress.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        except Exception:  # noqa: BLE001 - stop recording rather than fail training
            self._progress = None

    @contextlib.contextmanager
    def phase(self, name: str, **fields: Any):
        self.record(name, edge="begin", **fields)
        yield
        self.record(name, edge="end", **fields)

    def step(self, **fields: Any) -> None:
        self._steps += 1
        if self._steps <= MAX_STEP_RECORDS:
            self.record("step", **fields)

    def finish(self, error: BaseException | None) -> None:
        if error is None:
            self.record("return", threads=_thread_count())
        else:
            self.record("raise", type=type(error).__name__, message=str(error)[:512])
        if self._stacks is not None:
            # Replaces the periodic dump: a healthy worker exits well before this.
            with contextlib.suppress(Exception):
                faulthandler.dump_traceback_later(EXIT_GRACE_SECONDS, file=self._stacks)


def _run_rank(plan: dict) -> dict | None:
    """Run one prepared executor rank. Rank zero returns bounded metadata only."""
    exact_keys(
        plan,
        {
            "schema_version",
            "kind",
            "run_id",
            "mode",
            "world_size",
            "program",
            "manifest_path",
            "dataset",
            "assignment",
            "schedule",
            "output_dir",
            "checkpoint_root",
            "resume",
            "runtime_identity",
            "timeout_seconds",
            "plan_digest",
        },
        name="training plan",
    )
    body = {key: value for key, value in plan.items() if key != "plan_digest"}
    if (
        plan["kind"] != "ds60-torch-training-plan"
        or plan["schema_version"] != 1
        or digest(body) != plan["plan_digest"]
    ):
        raise TrainingError("Worker received a changed training plan")
    world = integer(plan["world_size"], "world size", 1, 2)
    if (plan["mode"], world) not in {("executor_single", 1), ("executor_ddp", 2)}:
        raise TrainingError("Unsupported executor training mode")
    rank = _rank_environment(world)
    diagnostics = _RankDiagnostics.start(plan, rank)
    try:
        result = _train_rank(plan, world, rank, diagnostics)
    except BaseException as error:
        diagnostics.finish(error)
        raise
    diagnostics.finish(None)
    return result


def _train_rank(plan: dict, world: int, rank: int, diagnostics: _RankDiagnostics) -> dict | None:
    import numpy as np
    import torch
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel

    _admit_runtime_identity(plan["runtime_identity"])
    if data.load_manifest(plan["manifest_path"]) != plan["dataset"]:
        raise TrainingError("Executor snapshot manifest differs from plan")
    if data._assignment(plan["assignment"], plan["dataset"]) != plan["assignment"]:
        raise TrainingError("Executor rank assignment changed")
    program = TrainingProgram.from_descriptor(plan["program"])
    if plan["program"]["feature_names"] != plan["dataset"]["feature_names"]:
        raise TrainingError("Executor program feature order differs from snapshot")
    if (plan["program"]["target_domain"] == "class_index") != (
        plan["dataset"]["label_kind"] == "class_index"
    ):
        raise TrainingError("Executor target domain differs from snapshot")
    schedule = plan["schedule"]
    if schedule != make_schedule(
        plan["assignment"],
        epochs=schedule["epochs"],
        steps_per_epoch=schedule["steps_per_epoch"],
        max_batch_rows=schedule["max_batch_rows"],
        seed=schedule["seed"],
    ):
        raise TrainingError("Training schedule changed")
    ranges = schedule["ranks"][rank]["ranges"]
    if schedule["ranks"][rank]["rank"] != rank or len(ranges) != schedule["steps_per_epoch"]:
        raise TrainingError("Rank schedule differs from logical rank")
    rows = list(data.iter_rank_rows(plan["manifest_path"], plan["assignment"], rank))
    assigned = plan["assignment"]["ranks"][rank]
    if len(rows) != assigned["rows"]:
        raise TrainingError("Rank data or schedule differs")
    expected_ranges = [
        [step * len(rows) // len(ranges), (step + 1) * len(rows) // len(ranges)]
        for step in range(len(ranges))
    ]
    if ranges != expected_ranges or any(
        end <= start or end - start > schedule["max_batch_rows"] for start, end in ranges
    ):
        raise TrainingError("Rank schedule cannot cover each row exactly once")
    torch.set_num_threads(1)
    rank_seed = schedule["seed"] + rank
    random.seed(rank_seed)
    np.random.seed(rank_seed % (2**32))
    torch.manual_seed(rank_seed)
    model, loss, optimizer, dtype = _construct(program, plan["program"], torch)
    schema = torch_adapter.module_schema_digest(model)
    binding = {
        "schema_version": 1,
        "kind": checkpoint.BINDING_KIND,
        "definition_digest": digest({"program": plan["program"], "module_schema_digest": schema}),
        "code_digest": plan["program"]["code_digest"],
        "runtime_digest": digest(plan["runtime_identity"]),
        "dataset_digest": plan["dataset"]["dataset_digest"],
        "assignment_digest": plan["assignment"]["assignment_digest"],
        "schedule_digest": schedule["schedule_digest"],
        "world_size": world,
        "model_layout": torch_adapter.model_layout(model),
        "optimizer_layout": torch_adapter.optimizer_layout(model, optimizer),
        "loss_state_digest": torch_adapter.loss_state_digest(loss),
    }
    checkpoint.validate_binding(binding)
    binding_digest = checkpoint.digest_value(binding)
    diagnostics.record(
        "model_ready",
        rows=len(rows),
        torch_threads=torch.get_num_threads(),
        threads=_thread_count(),
    )
    if world == 2:
        with diagnostics.phase(
            "init_process_group",
            master_addr=os.environ.get("MASTER_ADDR"),
            master_port=os.environ.get("MASTER_PORT"),
            gloo_socket_ifname=os.environ.get("GLOO_SOCKET_IFNAME"),
        ):
            dist.init_process_group(
                "gloo",
                init_method="env://",
                rank=rank,
                world_size=world,
                timeout=timedelta(seconds=60),
            )
    try:
        if world == 2:
            with diagnostics.phase("gather_identities"):
                identities = _all_gather(
                    dist, {"binding_digest": binding_digest, "schema": schema}, world
                )
            if len({item["binding_digest"] for item in identities}) != 1:
                raise TrainingError("Rank model/loss/optimizer definitions differ")
        with diagnostics.phase("wrap_model"):
            train_model = (
                DistributedDataParallel(model, device_ids=None, broadcast_buffers=False)
                if world == 2
                else model
            )
        start_epoch = 0
        global_step = 0
        parent_digest = None
        if plan["resume"] is not None:
            reference = plan["resume"]
            with diagnostics.phase("restore_checkpoint"):
                loaded = checkpoint.load_rank(
                    reference["path"],
                    expected_binding=binding,
                    expected_manifest_digest=reference["manifest_digest"],
                    rank=rank,
                )
                optimizer.zero_grad(set_to_none=True)
                torch_adapter.restore_rank_state(
                    model,
                    optimizer,
                    loss,
                    loaded,
                    expected_binding=binding,
                    expected_module_schema_digest=schema,
                )
            start_epoch = loaded.progress["epoch"] + 1
            global_step = loaded.progress["global_step"]
            parent_digest = reference["manifest_digest"]
        verified_files = [
            item for item in plan["dataset"]["files"] if item["path"] in assigned["files"]
        ]
        ordered_files = [
            next(item for item in verified_files if item["path"] == name)
            for name in assigned["files"]
        ]
        latest = None
        checkpoint_count = 0
        final_ledger = None
        for epoch in range(start_epoch, schedule["epochs"]):
            delivered = []
            for begin, end in ranges:
                batch = rows[begin:end]
                if not batch:
                    raise TrainingError("Every rank must participate in every step")
                diagnostics.step(epoch=epoch, global_step=global_step, batch_rows=len(batch))
                optimizer.zero_grad(set_to_none=True)
                local_sum, local_mass = _batch_loss(
                    train_model,
                    loss,
                    batch,
                    plan["program"]["target_domain"],
                    dtype,
                    torch,
                )
                if world == 2:
                    dist.all_reduce(local_mass, op=dist.ReduceOp.SUM)
                if not torch.isfinite(local_mass).item() or local_mass.item() <= 0:
                    raise TrainingError("Global step weight mass must be finite and positive")
                objective = local_sum * (world / local_mass)
                if not torch.isfinite(objective).item():
                    raise TrainingError("Nonfinite training objective")
                objective.backward()
                if any(
                    parameter.grad is None or not torch.isfinite(parameter.grad).all().item()
                    for parameter in model.parameters()
                    if parameter.requires_grad
                ):
                    raise TrainingError("Missing or nonfinite model gradient")
                optimizer.step()
                if any(
                    not torch.isfinite(parameter).all().item() for parameter in model.parameters()
                ):
                    raise TrainingError("Nonfinite model update")
                global_step += 1
                delivered.extend(batch)
            if delivered != rows:
                raise TrainingError("Epoch row delivery differs from admitted fixed order")
            optimizer.zero_grad(set_to_none=True)
            final_ledger = ledger(delivered, len(ranges))
            progress = {
                "boundary": "completed_epoch",
                "epoch": epoch,
                "global_step": global_step,
                "epoch_steps": len(ranges),
            }
            sampler = {
                "kind": "fixed_order_v1",
                "seed": None,
                "next_epoch": epoch + 1,
                "cursor": 0,
                "generator_names": [],
            }
            state = torch_adapter.capture_rank_state(
                model,
                optimizer,
                loss,
                expected_binding=binding,
                expected_module_schema_digest=schema,
                progress=progress,
                sampler=sampler,
            )
            with diagnostics.phase("gather_ledgers", epoch=epoch):
                ledgers = _all_gather(dist, final_ledger, world) if world == 2 else [final_ledger]
            if rank == 0:
                with diagnostics.phase("begin_checkpoint", epoch=epoch):
                    transaction = checkpoint.begin_checkpoint(
                        Path(plan["checkpoint_root"]),
                        f"epoch-{epoch:04d}",
                        binding,
                        progress,
                        ledgers,
                        run_id=plan["run_id"],
                        attempt_id=plan["run_id"],
                        parent_manifest_digest=parent_digest,
                    )
                transaction_value = asdict(transaction)
            else:
                transaction_value = None
            if world == 2:
                with diagnostics.phase("broadcast_transaction", epoch=epoch):
                    transaction_value = _broadcast(dist, transaction_value, rank)
            transaction = checkpoint.Transaction(**transaction_value)
            with diagnostics.phase("write_rank_checkpoint", epoch=epoch):
                ack = checkpoint.write_rank(transaction, rank, state, ledger=final_ledger)
            with diagnostics.phase("gather_acknowledgments", epoch=epoch):
                acknowledgments = (
                    _all_gather(dist, asdict(ack), world) if world == 2 else [asdict(ack)]
                )
            if rank == 0:
                with diagnostics.phase("commit_checkpoint", epoch=epoch):
                    latest = checkpoint.commit_checkpoint(
                        transaction,
                        [checkpoint.RankAck(**item) for item in acknowledgments],
                    )
                reference_value = asdict(latest)
            else:
                reference_value = None
            if world == 2:
                with diagnostics.phase("broadcast_reference", epoch=epoch):
                    reference_value = _broadcast(dist, reference_value, rank)
            latest = checkpoint.CheckpointRef(**reference_value)
            parent_digest = latest.manifest_digest
            checkpoint_count += 1
        if final_ledger is None or latest is None:
            raise TrainingError("Training attempt made no new complete epoch")
        replica = checkpoint.replica_digest(state, binding)
        receipt = {
            "rank": rank,
            "world_size": world,
            "hostname": socket.gethostname(),
            "host_addresses": _addresses(socket.gethostname()),
            "pid": os.getpid(),
            "program_digest": plan["program"]["program_digest"],
            "dataset_digest": plan["dataset"]["dataset_digest"],
            "assignment_digest": plan["assignment"]["assignment_digest"],
            "schedule_digest": schedule["schedule_digest"],
            "runtime_digest": digest(plan["runtime_identity"]),
            "binding_digest": binding_digest,
            "module_schema_digest": schema,
            "model_parameter_digest": _tensor_digest(model),
            "optimizer_replica_digest": replica,
            "start_epoch": start_epoch,
            "completed_epochs": schedule["epochs"],
            "global_step": global_step,
            "epoch_ledger": final_ledger,
            "row_deliveries_this_attempt": (schedule["epochs"] - start_epoch) * len(rows),
            "checkpoint_count": checkpoint_count,
            "verified_files": ordered_files,
            "latest_checkpoint": asdict(latest),
            "execution_policy": {
                "device": "cpu",
                "torch_threads": 1,
                "data_workers": 0,
                "sampler": "fixed_order_v1",
                "gradient_accumulation": 1,
            },
            "rank_seed": rank_seed,
            "mode": plan["mode"],
        }
        with diagnostics.phase("gather_receipts"):
            receipts = _all_gather(dist, receipt, world) if world == 2 else [receipt]
        if rank != 0:
            return None
        result = {
            "schema_version": 1,
            "kind": "ds60-torch-training-worker-result",
            "status": "completed",
            "plan_digest": plan["plan_digest"],
            "program_digest": plan["program"]["program_digest"],
            "dataset_digest": plan["dataset"]["dataset_digest"],
            "assignment_digest": plan["assignment"]["assignment_digest"],
            "schedule_digest": schedule["schedule_digest"],
            "runtime_digest": digest(plan["runtime_identity"]),
            "world_size": world,
            "completed_epochs": schedule["epochs"],
            "global_step": global_step,
            "rank_receipts": receipts,
            "latest_checkpoint": asdict(latest),
        }
        canonical_json(result, limit=MAX_RECEIPT)
        return result
    finally:
        if world == 2 and dist.is_initialized():
            with diagnostics.phase("destroy_process_group"):
                dist.destroy_process_group()
