# SPDX-License-Identifier: Apache-2.0
"""Work-only, data-only epoch checkpoints for explicitly bound CPU training.

No pickle, model import, automatic resume or training-success claim is provided.
An atomic COMMITTED marker publishes already verified rank files. A failure after
that publication is ambiguous to the writer and requires explicit readback.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import struct
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BINDING_KIND = "torch_training_checkpoint_binding_v1"
TRANSACTION_KIND = "torch_training_checkpoint_transaction_v1"
COMMIT_KIND = "torch_training_checkpoint_commit_v1"
SHA = re.compile(r"[a-f0-9]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
DTYPES = {
    "float32": (4, "f"),
    "float64": (8, "d"),
    "int64": (8, "q"),
    "int32": (4, "i"),
    "uint64": (8, "Q"),
    "uint32": (4, "I"),
    "uint8": (1, "B"),
    "bool": (1, "B"),
}
DIGEST_FIELDS = {
    "definition_digest",
    "code_digest",
    "runtime_digest",
    "dataset_digest",
    "assignment_digest",
    "schedule_digest",
    "loss_state_digest",
}
BINDING_FIELDS = DIGEST_FIELDS | {
    "schema_version",
    "kind",
    "world_size",
    "model_layout",
    "optimizer_layout",
}
MAX_JSON = 4 * 1024 * 1024
MAX_TENSOR = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_TENSORS = 16384
MAX_NODES = 100_000
MAX_RANKS = 32


class CheckpointError(ValueError):
    pass


class AmbiguousCommit(CheckpointError):
    """The publish point may have succeeded. Never retry or overwrite automatically."""

    def __init__(self, message: str, reference: CheckpointRef):
        super().__init__(message)
        self.reference = reference


@dataclass(frozen=True)
class TensorData:
    dtype: str
    shape: tuple[int, ...]
    data: bytes


@dataclass(frozen=True)
class Transaction:
    path: str
    transaction_digest: str


@dataclass(frozen=True)
class RankAck:
    rank: int
    ready_digest: str
    replica_digest: str


@dataclass(frozen=True)
class CheckpointRef:
    path: str
    manifest_digest: str
    transaction_digest: str
    training_run_status: str = "not_attested"


@dataclass(frozen=True)
class LoadedRank:
    reference: CheckpointRef
    binding: dict[str, Any]
    progress: dict[str, Any]
    ledger: dict[str, Any]
    state: dict[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_value(value: Any) -> str:
    return sha(json_bytes(value))


def json_bytes(value: Any) -> bytes:
    raw = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    require(len(raw) <= MAX_JSON, "JSON exceeds checkpoint bound")
    return raw


def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in items:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def safe_path(path: Path | str) -> Path:
    require(
        type(path) is str or isinstance(path, Path),
        "Checkpoint path must be Path or string",
    )
    path = Path(path).absolute()
    require(".." not in path.parts, "Parent traversal is forbidden")
    for item in [*reversed(path.parents), path]:
        try:
            mode = item.lstat().st_mode
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(mode), "Symlink component is forbidden")
        require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), "Special file is forbidden")
    return path


def read_bytes(path: Path, limit: int, *, allow_links: bool = False) -> bytes:
    safe_path(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode), "Expected regular checkpoint file")
        require(allow_links or info.st_nlink == 1, "Aliased checkpoint file is forbidden")
        require(info.st_size <= limit, "Checkpoint file exceeds byte bound")
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "Checkpoint file exceeds actual read bound")
    return raw


def parse_json(raw: bytes) -> dict[str, Any]:
    def nonfinite(_: str) -> None:
        raise CheckpointError("Nonfinite JSON is forbidden")

    require(len(raw) <= MAX_JSON, "JSON exceeds actual byte bound")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=nonfinite)
    require(type(value) is dict, "Expected checkpoint JSON object")
    assert isinstance(value, dict)
    return value


def read_json(path: Path, *, allow_links: bool = False) -> dict[str, Any]:
    return parse_json(read_bytes(path, MAX_JSON, allow_links=allow_links))


def write_new(path: Path, raw: bytes) -> None:
    safe_path(path)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def sync_directory(path: Path) -> None:
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def valid_name(value: Any) -> bool:
    return (
        type(value) is str
        and 0 < len(value.encode("utf-8")) <= 512
        and not any(ord(c) < 32 for c in value)
    )


def integer(value: Any, minimum: int = 0, maximum: int = 2**53 - 1) -> bool:
    return type(value) is int and minimum <= value <= maximum


def finite(value: Any, *, nonnegative: bool = False) -> bool:
    return type(value) in {int, float} and math.isfinite(value) and (not nonnegative or value >= 0)


def checked_tensor(value: Any) -> TensorData:
    require(type(value) is TensorData, "Only explicit raw TensorData is supported")
    assert isinstance(value, TensorData)
    require(
        value.dtype in DTYPES and type(value.shape) is tuple and len(value.shape) <= 8,
        "Unsupported tensor dtype or shape",
    )
    require(
        all(integer(d, maximum=2**31 - 1) for d in value.shape),
        "Invalid tensor dimension",
    )
    size = math.prod(value.shape) * DTYPES[value.dtype][0]
    require(
        size <= MAX_TENSOR and type(value.data) is bytes and len(value.data) == size,
        "Tensor byte length or shape mismatch",
    )
    if value.dtype in {"float32", "float64"}:
        require(
            all(
                math.isfinite(item[0])
                for item in struct.iter_unpack("<" + DTYPES[value.dtype][1], value.data)
            ),
            "Nonfinite tensor state is unsupported",
        )
    elif value.dtype == "bool":
        require(all(item in {0, 1} for item in value.data), "Noncanonical bool tensor")
    return value


def validate_binding(binding: Any) -> dict[str, Any]:
    require(
        type(binding) is dict and set(binding) == BINDING_FIELDS,
        "Unknown checkpoint binding schema",
    )
    require(
        type(binding["schema_version"]) is int
        and binding["schema_version"] == 1
        and binding["kind"] == BINDING_KIND,
        "Unknown checkpoint binding version",
    )
    require(
        all(type(binding[key]) is str and SHA.fullmatch(binding[key]) for key in DIGEST_FIELDS),
        "Every source/data/runtime identity needs SHA256",
    )
    require(integer(binding["world_size"], 1, MAX_RANKS), "Invalid fixed world size")
    layout = binding["model_layout"]
    require(
        type(layout) is list and 0 < len(layout) <= MAX_TENSORS,
        "Bounded model layout is required",
    )
    names = []
    trainable = []
    for item in layout:
        require(
            type(item) is dict and set(item) == {"name", "role", "dtype", "shape", "requires_grad"},
            "Unknown model state layout",
        )
        require(
            valid_name(item["name"]) and item["role"] in {"parameter", "buffer"},
            "Invalid model state name/role",
        )
        require(
            item["dtype"] in DTYPES
            and type(item["shape"]) is list
            and len(item["shape"]) <= 8
            and all(integer(d, maximum=2**31 - 1) for d in item["shape"]),
            "Invalid declared tensor shape/dtype",
        )
        require(
            math.prod(item["shape"]) * DTYPES[item["dtype"]][0] <= MAX_TENSOR,
            "Declared tensor exceeds bound",
        )
        require(type(item["requires_grad"]) is bool, "Invalid requires_grad flag")
        if item["role"] == "buffer":
            require(not item["requires_grad"], "Differentiable buffers are unsupported")
        else:
            require(
                item["dtype"] in {"float32", "float64"} and math.prod(item["shape"]) > 0,
                "Only nonempty floating CPU parameters are supported",
            )
            if item["requires_grad"]:
                trainable.append(item["name"])
        names.append(item["name"])
    require(len(names) == len(set(names)), "Duplicate model state name")
    optimizer = binding["optimizer_layout"]
    require(
        type(optimizer) is dict and set(optimizer) == {"class", "groups"},
        "Unknown optimizer layout",
    )
    require(
        optimizer["class"] in {"torch.optim.SGD", "torch.optim.Adam", "torch.optim.AdamW"},
        "Optimizer class is not admitted",
    )
    require(
        type(optimizer["groups"]) is list and 0 < len(optimizer["groups"]) <= 256,
        "Bounded ordered optimizer groups are required",
    )
    grouped = []
    for group in optimizer["groups"]:
        require(
            type(group) is dict and set(group) == {"names", "options"},
            "Unknown optimizer group",
        )
        require(
            type(group["names"]) is list
            and bool(group["names"])
            and all(valid_name(name) for name in group["names"]),
            "Ordered optimizer names are required",
        )
        require(
            type(group["options"]) is dict and len(json_bytes(group["options"])) <= 16384,
            "Optimizer options exceed the configuration bound",
        )
        validate_optimizer_options(optimizer["class"], group["options"])
        grouped.extend(group["names"])
    require(
        len(grouped) == len(set(grouped)) and set(grouped) == set(trainable),
        "Optimizer groups must cover every trainable name exactly once",
    )
    # Names/order are bound as data; they are not inferred from PyTorch's positional IDs.
    return parse_json(json_bytes(binding))


def validate_optimizer_options(kind: str, options: dict[str, Any]) -> None:
    common = {"lr", "weight_decay", "maximize", "foreach", "differentiable", "fused"}
    extra = (
        {"momentum", "dampening", "nesterov"}
        if kind.endswith("SGD")
        else {"betas", "eps", "amsgrad", "capturable", "decoupled_weight_decay"}
    )
    require(
        set(options) <= common | extra and {"lr", "weight_decay"} <= set(options),
        "Unsupported or incomplete optimizer options",
    )
    for key in ("lr", "weight_decay", "momentum", "dampening", "eps"):
        if key in options:
            require(
                finite(options[key], nonnegative=True),
                "Optimizer scalar options must be finite and nonnegative",
            )
    for key in (
        "maximize",
        "nesterov",
        "amsgrad",
        "differentiable",
        "capturable",
        "decoupled_weight_decay",
    ):
        if key in options:
            require(type(options[key]) is bool, "Optimizer flag must be boolean")
    for key in ("foreach", "fused"):
        require(
            options.get(key) is None or type(options[key]) is bool,
            "Optimizer execution flag is invalid",
        )
    require(
        not options.get("fused")
        and not options.get("capturable")
        and not options.get("differentiable"),
        "Fused/capturable/differentiable state is not qualified",
    )
    if kind.endswith("SGD"):
        require(
            {"momentum", "dampening", "nesterov"} <= set(options),
            "SGD options are incomplete",
        )
        require(
            not options["nesterov"] or (options["momentum"] > 0 and options["dampening"] == 0),
            "Invalid Nesterov options",
        )
    else:
        require(
            {"betas", "eps", "amsgrad", "decoupled_weight_decay"} <= set(options),
            "Adam options are incomplete",
        )
        betas = options["betas"]
        require(
            type(betas) is list
            and len(betas) == 2
            and all(finite(v) and 0 <= v < 1 for v in betas),
            "Adam betas must be bounded scalar values",
        )
        require(
            kind != "torch.optim.AdamW" or options["decoupled_weight_decay"],
            "AdamW must retain decoupled decay",
        )


def validate_progress(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict and set(value) == {"boundary", "epoch", "global_step", "epoch_steps"},
        "Unknown checkpoint progress schema",
    )
    require(
        value["boundary"] == "completed_epoch"
        and integer(value["epoch"])
        and integer(value["global_step"], 1)
        and integer(value["epoch_steps"], 1),
        "Only a completed epoch boundary is supported",
    )
    require(
        value["global_step"] >= value["epoch_steps"],
        "Inconsistent completed step count",
    )
    return parse_json(json_bytes(value))


def validate_ledger(value: Any, progress: dict[str, Any]) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"row_count", "weight_sum", "membership_digest", "data_digest", "steps"},
        "Unknown rank data ledger",
    )
    require(
        integer(value["row_count"], 1) and finite(value["weight_sum"], nonnegative=True),
        "A rank needs positive rows and nonnegative weight mass",
    )
    require(
        integer(value["steps"], 1) and value["steps"] == progress["epoch_steps"],
        "Rank steps differ from the common epoch boundary",
    )
    require(
        all(
            type(value[k]) is str and SHA.fullmatch(value[k])
            for k in ("membership_digest", "data_digest")
        ),
        "Exact membership/data identities are required",
    )
    return parse_json(json_bytes(value))


def begin_checkpoint(
    root: Path,
    checkpoint_id: str,
    binding: dict[str, Any],
    progress: dict[str, Any],
    expected_ledgers: list[dict[str, Any]],
    *,
    run_id: str,
    attempt_id: str,
    parent_manifest_digest: str | None = None,
) -> Transaction:
    root = safe_path(root)
    require(root.is_dir(), "Use an existing owned checkpoint root")
    require(
        all(
            type(name) is str and ID.fullmatch(name) and name not in {".", ".."}
            for name in (checkpoint_id, run_id, attempt_id)
        ),
        "Invalid checkpoint/run/attempt identity",
    )
    binding = validate_binding(binding)
    progress = validate_progress(progress)
    require(
        type(expected_ledgers) is list and len(expected_ledgers) == binding["world_size"],
        "Every logical rank needs an expected data ledger",
    )
    ledgers = [validate_ledger(value, progress) for value in expected_ledgers]
    total_weight = math.fsum(value["weight_sum"] for value in ledgers)
    require(
        math.isfinite(total_weight) and total_weight > 0,
        "Global epoch weight mass must be positive and finite",
    )
    require(
        parent_manifest_digest is None
        or (
            type(parent_manifest_digest) is str
            and SHA.fullmatch(parent_manifest_digest) is not None
        ),
        "Invalid parent checkpoint identity",
    )
    directory = root / checkpoint_id
    require(
        not directory.exists() and not directory.is_symlink(),
        "Checkpoint paths are append-only; existing outcomes require readback",
    )
    directory.mkdir(mode=0o700)
    payload = {
        "schema_version": 1,
        "kind": TRANSACTION_KIND,
        "transaction_id": uuid.uuid4().hex,
        "checkpoint_id": checkpoint_id,
        "run_id": run_id,
        "attempt_id": attempt_id,
        "parent_manifest_digest": parent_manifest_digest,
        "binding": binding,
        "progress": progress,
        "expected_ledgers": ledgers,
    }
    raw = json_bytes(payload)
    write_new(directory / "transaction.json", raw)
    sync_directory(directory)
    sync_directory(root)
    return Transaction(str(directory), sha(raw))


def read_transaction(transaction: Transaction) -> tuple[Path, dict[str, Any]]:
    require(
        type(transaction) is Transaction
        and SHA.fullmatch(transaction.transaction_digest) is not None,
        "Invalid transaction handle",
    )
    directory = safe_path(Path(transaction.path))
    raw = read_bytes(directory / "transaction.json", MAX_JSON)
    require(sha(raw) == transaction.transaction_digest, "Transaction identity changed")
    payload = parse_json(raw)
    require(
        set(payload)
        == {
            "schema_version",
            "kind",
            "transaction_id",
            "checkpoint_id",
            "run_id",
            "attempt_id",
            "parent_manifest_digest",
            "binding",
            "progress",
            "expected_ledgers",
        }
        and type(payload["schema_version"]) is int
        and payload["schema_version"] == 1
        and payload["kind"] == TRANSACTION_KIND,
        "Unknown transaction schema",
    )
    require(
        directory.name == payload["checkpoint_id"],
        "Checkpoint directory identity differs",
    )
    require(
        all(
            type(payload[key]) is str
            and ID.fullmatch(payload[key]) is not None
            and payload[key] not in {".", ".."}
            for key in ("checkpoint_id", "run_id", "attempt_id")
        ),
        "Invalid transaction run/checkpoint identity",
    )
    require(
        type(payload["transaction_id"]) is str
        and re.fullmatch(r"[a-f0-9]{32}", payload["transaction_id"]) is not None,
        "Invalid transaction token",
    )
    parent = payload["parent_manifest_digest"]
    require(
        parent is None or (type(parent) is str and SHA.fullmatch(parent) is not None),
        "Invalid parent checkpoint identity",
    )
    validate_binding(payload["binding"])
    validate_progress(payload["progress"])
    require(
        len(payload["expected_ledgers"]) == payload["binding"]["world_size"],
        "Incomplete rank ledger manifest",
    )
    for value in payload["expected_ledgers"]:
        validate_ledger(value, payload["progress"])
    return directory, payload


def validate_state(state: Any, binding: dict[str, Any], progress: dict[str, Any]) -> None:
    require(
        type(state) is dict
        and set(state)
        == {
            "model",
            "optimizer",
            "rng",
            "sampler",
            "module_modes",
            "loss_state_digest",
        },
        "Unsupported or omitted training state",
    )
    require(
        state["loss_state_digest"] == binding["loss_state_digest"],
        "Loss state differs from immutable definition",
    )
    model = state["model"]
    require(
        type(model) is dict and list(model) == [r["name"] for r in binding["model_layout"]],
        "Named model state order differs",
    )
    by_name = {r["name"]: r for r in binding["model_layout"]}
    for name, value in model.items():
        tensor = checked_tensor(value)
        specification = by_name[name]
        require(
            tensor.dtype == specification["dtype"] and list(tensor.shape) == specification["shape"],
            "Model tensor layout differs: " + name,
        )
    modes = state["module_modes"]
    require(
        type(modes) is dict
        and "" in modes
        and len(modes) <= MAX_TENSORS
        and all(
            (name == "" or valid_name(name)) and type(mode) is bool for name, mode in modes.items()
        ),
        "Complete bounded module training modes are required",
    )
    optimizer = state["optimizer"]
    require(type(optimizer) is dict, "Optimizer state must be a named mapping")
    names = [name for group in binding["optimizer_layout"]["groups"] for name in group["names"]]
    require(
        list(optimizer) == [name for name in names if name in optimizer],
        "Unknown or reordered optimizer parameter state",
    )
    for group in binding["optimizer_layout"]["groups"]:
        for name in group["names"]:
            if name not in optimizer:
                continue
            item = optimizer[name]
            require(type(item) is dict, "Optimizer parameter state must be data")
            if not item:
                continue
            kind = binding["optimizer_layout"]["class"]
            keys = (
                {"momentum_buffer"}
                if kind.endswith("SGD")
                else {"step", "exp_avg", "exp_avg_sq"}
                | ({"max_exp_avg_sq"} if group["options"]["amsgrad"] else set())
            )
            require(set(item) == keys, "Unsupported optimizer state fields")
            if kind.endswith("SGD"):
                require(group["options"]["momentum"] > 0, "Unexpected momentum state")
            for key, value in item.items():
                tensor = checked_tensor(value)
                if key == "step":
                    require(
                        tensor.dtype in {"float32", "float64"} and tensor.shape == (),
                        "Adam step must be a scalar CPU tensor",
                    )
                    step = struct.unpack("<" + DTYPES[tensor.dtype][1], tensor.data)[0]
                    require(
                        step == int(step) and 0 <= step <= progress["global_step"],
                        "Invalid optimizer step identity",
                    )
                else:
                    require(
                        tensor.dtype == by_name[name]["dtype"]
                        and list(tensor.shape) == by_name[name]["shape"],
                        "Optimizer tensor shape/dtype differs",
                    )
    sampler = state["sampler"]
    require(
        type(sampler) is dict
        and set(sampler) == {"kind", "seed", "next_epoch", "cursor", "generator_names"},
        "Unsupported sampler state",
    )
    require(
        sampler["kind"] in {"fixed_order_v1", "epoch_seeded_permutation_v1"},
        "Unknown sampler kind",
    )
    require(
        (
            sampler["seed"] is None
            if sampler["kind"] == "fixed_order_v1"
            else integer(sampler["seed"], maximum=2**63 - 1)
        ),
        "Invalid explicit sampler seed",
    )
    require(
        sampler["next_epoch"] == progress["epoch"] + 1
        and type(sampler["next_epoch"]) is int
        and type(sampler["cursor"]) is int
        and sampler["cursor"] == 0,
        "Sampler is not at the next complete epoch boundary",
    )
    require(
        type(sampler["generator_names"]) is list
        and len(sampler["generator_names"]) <= 64
        and len(sampler["generator_names"]) == len(set(sampler["generator_names"]))
        and all(valid_name(n) for n in sampler["generator_names"]),
        "Invalid named RNG stream set",
    )
    rng = state["rng"]
    require(
        type(rng) is dict and set(rng) == {"python", "numpy", "torch_cpu", "generators"},
        "Every supported RNG domain must be represented",
    )
    py = rng["python"]
    require(
        type(py) is tuple
        and len(py) == 3
        and type(py[0]) is int
        and py[0] == 3
        and type(py[1]) is tuple
        and len(py[1]) == 625,
        "Unsupported Python RNG state",
    )
    require(
        all(integer(x, maximum=2**32 - 1) for x in py[1][:-1])
        and integer(py[1][-1], maximum=624)
        and (py[2] is None or finite(py[2])),
        "Invalid Python RNG words/cache",
    )
    np = rng["numpy"]
    require(
        type(np) is tuple and len(np) == 5 and np[0] == "MT19937" and type(np[0]) is str,
        "Only explicit NumPy MT19937 state is admitted",
    )
    words = checked_tensor(np[1])
    require(
        words.dtype == "uint32"
        and words.shape == (624,)
        and integer(np[2], maximum=624)
        and type(np[3]) is int
        and np[3] in {0, 1}
        and finite(np[4]),
        "Invalid NumPy RNG state",
    )
    generators = rng["generators"]
    require(
        type(generators) is dict and list(generators) == sampler["generator_names"],
        "Explicit generator RNG names/order differ",
    )
    for value in [rng["torch_cpu"], *generators.values()]:
        tensor = checked_tensor(value)
        require(
            tensor.dtype == "uint8" and len(tensor.shape) == 1 and 1 <= len(tensor.data) <= 65536,
            "Torch CPU RNG must be bounded raw bytes",
        )


def encode_state(
    state: dict[str, Any],
) -> tuple[Any, list[tuple[dict[str, Any], bytes]]]:
    files: list[tuple[dict[str, Any], bytes]] = []
    nodes = 0
    total = 0

    def visit(value: Any, depth: int = 0) -> Any:
        nonlocal nodes, total
        nodes += 1
        require(nodes <= MAX_NODES and depth <= 16, "State tree exceeds bound")
        if type(value) is TensorData:
            checked_tensor(value)
            index = len(files)
            require(index < MAX_TENSORS, "Too many state tensors")
            total += len(value.data)
            require(total <= MAX_TOTAL, "Rank tensor bytes exceed bound")
            item = {
                "path": f"tensor-{index:05d}.bin",
                "dtype": value.dtype,
                "shape": list(value.shape),
                "bytes": len(value.data),
                "sha256": sha(value.data),
            }
            files.append((item, value.data))
            return {"kind": "tensor", "index": index}
        if type(value) is dict:
            require(
                len(value) <= MAX_TENSORS
                and all(type(key) is str and (key == "" or valid_name(key)) for key in value),
                "State mapping keys/count unsupported",
            )
            return {
                "kind": "dict",
                "items": [[key, visit(item, depth + 1)] for key, item in value.items()],
            }
        if type(value) in {list, tuple}:
            require(len(value) <= MAX_TENSORS, "State sequence exceeds bound")
            return {
                "kind": "tuple" if type(value) is tuple else "list",
                "items": [visit(item, depth + 1) for item in value],
            }
        if value is None:
            return {"kind": "none"}
        if type(value) is bool:
            return {"kind": "bool", "value": value}
        if type(value) is int:
            require(abs(value) < 2**128, "State integer exceeds bound")
            return {"kind": "int", "value": str(value)}
        if type(value) is float:
            require(math.isfinite(value), "Nonfinite scalar state")
            return {"kind": "float", "value": value.hex()}
        if type(value) is str:
            require(len(value.encode()) <= 16384, "State string exceeds bound")
            return {"kind": "str", "value": value}
        raise CheckpointError("Executable/custom state objects are unsupported")

    tree = visit(state)
    json_bytes(tree)
    return tree, files


def decode_state(tree: Any, tensors: list[TensorData]) -> dict[str, Any]:
    nodes = 0
    used = []

    def visit(value: Any, depth: int = 0) -> Any:
        nonlocal nodes
        nodes += 1
        require(
            nodes <= MAX_NODES
            and depth <= 16
            and type(value) is dict
            and type(value.get("kind")) is str,
            "Invalid state tree",
        )
        kind = value["kind"]
        if kind == "tensor":
            require(
                set(value) == {"kind", "index"}
                and integer(value["index"], maximum=len(tensors) - 1),
                "Invalid tensor reference",
            )
            used.append(value["index"])
            return tensors[value["index"]]
        if kind in {"dict", "list", "tuple"}:
            require(
                set(value) == {"kind", "items"}
                and type(value["items"]) is list
                and len(value["items"]) <= MAX_TENSORS,
                "Invalid container state",
            )
            if kind == "dict":
                result = {}
                for pair in value["items"]:
                    require(
                        type(pair) is list
                        and len(pair) == 2
                        and type(pair[0]) is str
                        and pair[0] not in result,
                        "Duplicate/invalid state mapping key",
                    )
                    result[pair[0]] = visit(pair[1], depth + 1)
                return result
            sequence = [visit(item, depth + 1) for item in value["items"]]
            return tuple(sequence) if kind == "tuple" else sequence
        if kind == "none":
            require(set(value) == {"kind"}, "Invalid null state")
            return None
        require(set(value) == {"kind", "value"}, "Unknown scalar state")
        scalar = value["value"]
        if kind == "bool":
            require(type(scalar) is bool, "Invalid bool state")
            return scalar
        if kind == "str":
            require(
                type(scalar) is str and len(scalar.encode()) <= 16384,
                "Invalid string state",
            )
            return scalar
        if kind == "int":
            require(
                type(scalar) is str and re.fullmatch(r"-?(0|[1-9][0-9]{0,38})", scalar) is not None,
                "Invalid integer state",
            )
            integer_value = int(scalar)
            require(
                abs(integer_value) < 2**128 and str(integer_value) == scalar,
                "Noncanonical integer state",
            )
            return integer_value
        if kind == "float":
            require(type(scalar) is str and len(scalar) <= 64, "Invalid float state")
            float_value = float.fromhex(scalar)
            require(
                math.isfinite(float_value) and float_value.hex() == scalar,
                "Noncanonical float state",
            )
            return float_value
        raise CheckpointError("Unknown executable/custom state tag")

    state = visit(tree)
    require(
        type(state) is dict and sorted(used) == list(range(len(tensors))),
        "Missing, duplicated or aliased tensor references",
    )
    assert isinstance(state, dict)
    return state


def replica_digest(state: dict[str, Any], binding: dict[str, Any]) -> str:
    replica = {
        "parameters": {
            r["name"]: state["model"][r["name"]]
            for r in binding["model_layout"]
            if r["role"] == "parameter"
        },
        "optimizer": state["optimizer"],
        "module_modes": state["module_modes"],
        "loss_state_digest": state["loss_state_digest"],
    }
    tree, files = encode_state(replica)
    return digest_value({"tree": tree, "tensors": [item for item, _ in files]})


def write_rank(
    transaction: Transaction,
    rank: int,
    state: dict[str, Any],
    *,
    ledger: dict[str, Any],
) -> RankAck:
    directory, tx = read_transaction(transaction)
    require(
        not (directory / "COMMITTED.json").exists() and not (directory / "manifest.json").exists(),
        "Checkpoint is already committed or outcome requires reconciliation",
    )
    require(integer(rank, maximum=tx["binding"]["world_size"] - 1), "Invalid logical rank")
    require(
        validate_ledger(ledger, tx["progress"]) == tx["expected_ledgers"][rank],
        "Actual rank data ledger differs from expected snapshot/schedule",
    )
    validate_state(state, tx["binding"], tx["progress"])
    tree, files = encode_state(state)
    rank_dir = directory / f"rank-{rank:05d}"
    rank_dir.mkdir(mode=0o700)
    for item, raw in files:
        write_new(rank_dir / item["path"], raw)
    state_raw = json_bytes(tree)
    write_new(rank_dir / "state.json", state_raw)
    replica = replica_digest(state, tx["binding"])
    ready = {
        "schema_version": 1,
        "kind": "torch_training_rank_checkpoint_v1",
        "rank": rank,
        "transaction_digest": transaction.transaction_digest,
        "progress": tx["progress"],
        "ledger": ledger,
        "state_digest": sha(state_raw),
        "tensors": [item for item, _ in files],
        "replica_digest": replica,
    }
    raw = json_bytes(ready)
    write_new(rank_dir / "READY.json", raw)
    sync_directory(rank_dir)
    sync_directory(directory)
    return RankAck(rank, sha(raw), replica)


def verify_rank(
    directory: Path,
    tx: dict[str, Any],
    transaction_digest: str,
    ack: RankAck,
    *,
    remaining_bytes: int = MAX_TOTAL,
) -> dict[str, Any]:
    require(
        type(ack) is RankAck
        and integer(ack.rank, maximum=tx["binding"]["world_size"] - 1)
        and SHA.fullmatch(ack.ready_digest) is not None
        and SHA.fullmatch(ack.replica_digest) is not None,
        "Invalid rank acknowledgment",
    )
    rank_dir = directory / f"rank-{ack.rank:05d}"
    raw = read_bytes(rank_dir / "READY.json", MAX_JSON)
    require(sha(raw) == ack.ready_digest, "Rank acknowledgment digest differs")
    ready = parse_json(raw)
    require(
        set(ready)
        == {
            "schema_version",
            "kind",
            "rank",
            "transaction_digest",
            "progress",
            "ledger",
            "state_digest",
            "tensors",
            "replica_digest",
        }
        and type(ready["schema_version"]) is int
        and ready["schema_version"] == 1
        and ready["kind"] == "torch_training_rank_checkpoint_v1",
        "Unknown rank checkpoint schema",
    )
    require(
        ready["rank"] == ack.rank
        and type(ready["rank"]) is int
        and ready["transaction_digest"] == transaction_digest
        and ready["progress"] == tx["progress"]
        and ready["ledger"] == tx["expected_ledgers"][ack.rank]
        and ready["replica_digest"] == ack.replica_digest,
        "Rank/progress/data identity differs",
    )
    validate_progress(ready["progress"])
    validate_ledger(ready["ledger"], tx["progress"])
    state_raw = read_bytes(rank_dir / "state.json", MAX_JSON)
    require(sha(state_raw) == ready["state_digest"], "Rank state hash mismatch")
    require(
        type(ready["tensors"]) is list and len(ready["tensors"]) <= MAX_TENSORS,
        "Invalid tensor inventory",
    )
    tensors = []
    expected = {"READY.json", "state.json"}
    total = len(raw) + len(state_raw)
    require(total <= remaining_bytes, "Complete checkpoint exceeds byte bound")
    for index, item in enumerate(ready["tensors"]):
        require(
            type(item) is dict
            and set(item) == {"path", "dtype", "shape", "bytes", "sha256"}
            and item["path"] == f"tensor-{index:05d}.bin",
            "Unsafe or reordered tensor file",
        )
        require(
            integer(item["bytes"], maximum=MAX_TENSOR)
            and type(item["shape"]) is list
            and type(item["sha256"]) is str
            and SHA.fullmatch(item["sha256"]) is not None,
            "Malformed tensor metadata",
        )
        require(
            total + item["bytes"] <= remaining_bytes,
            "Complete checkpoint exceeds byte bound",
        )
        data = read_bytes(rank_dir / item["path"], MAX_TENSOR)
        require(
            len(data) == item["bytes"] and sha(data) == item["sha256"],
            "Tensor hash/length mismatch",
        )
        tensor = checked_tensor(TensorData(item["dtype"], tuple(item["shape"]), data))
        tensors.append(tensor)
        total += len(data)
        require(total <= MAX_TOTAL, "Rank payload exceeds bound")
        expected.add(item["path"])
    require(
        {p.name for p in rank_dir.iterdir()} == expected,
        "Unknown or missing rank payload files",
    )
    state = decode_state(parse_json(state_raw), tensors)
    validate_state(state, tx["binding"], tx["progress"])
    require(
        replica_digest(state, tx["binding"]) == ack.replica_digest,
        "Replica state differs from acknowledgment",
    )
    return {"state": state, "bytes": total, "ready": ready}


def commit_checkpoint(transaction: Transaction, acknowledgments: list[RankAck]) -> CheckpointRef:
    directory, tx = read_transaction(transaction)
    world = tx["binding"]["world_size"]
    require(
        type(acknowledgments) is list
        and len(acknowledgments) == world
        and all(type(a) is RankAck for a in acknowledgments)
        and [a.rank for a in acknowledgments] == list(range(world)),
        "Every logical rank must acknowledge once in order",
    )
    require(
        not (directory / "manifest.json").exists() and not (directory / "COMMITTED.json").exists(),
        "Existing commit outcome must be reconciled, never overwritten",
    )
    require(
        {p.name for p in directory.iterdir()}
        == {"transaction.json", *[f"rank-{r:05d}" for r in range(world)]},
        "Partial or unexpected checkpoint directory",
    )
    total = 0
    for ack in acknowledgments:
        checked = verify_rank(
            directory,
            tx,
            transaction.transaction_digest,
            ack,
            remaining_bytes=MAX_TOTAL - total,
        )
        total += checked["bytes"]
        del checked
    require(
        len({ack.replica_digest for ack in acknowledgments}) == 1,
        "Parameters/optimizer replicas disagree at the epoch boundary",
    )
    manifest = {
        "schema_version": 1,
        "kind": "torch_training_checkpoint_manifest_v1",
        "transaction_digest": transaction.transaction_digest,
        "binding": tx["binding"],
        "progress": tx["progress"],
        "ranks": [
            {
                "rank": ack.rank,
                "ready_digest": ack.ready_digest,
                "replica_digest": ack.replica_digest,
            }
            for ack in acknowledgments
        ],
        "training_run_status": "not_attested",
    }
    raw = json_bytes(manifest)
    write_new(directory / "manifest.json", raw)
    sync_directory(directory)
    # Recheck after manifest writing, before the atomic publication point.
    total = 0
    for ack in acknowledgments:
        checked = verify_rank(
            directory,
            tx,
            transaction.transaction_digest,
            ack,
            remaining_bytes=MAX_TOTAL - total,
        )
        total += checked["bytes"]
        del checked
    commit = json_bytes(
        {
            "schema_version": 1,
            "kind": COMMIT_KIND,
            "manifest_digest": sha(raw),
            "transaction_digest": transaction.transaction_digest,
        }
    )
    temporary = directory.parent / (".commit-" + uuid.uuid4().hex + ".json")
    write_new(temporary, commit)
    reference = CheckpointRef(str(directory), sha(raw), transaction.transaction_digest)
    published = False
    try:
        os.link(temporary, directory / "COMMITTED.json", follow_symlinks=False)
        published = True
        sync_directory(directory)
        load_rank(
            directory,
            expected_binding=tx["binding"],
            expected_manifest_digest=reference.manifest_digest,
            rank=0,
        )
        temporary.unlink()
        sync_directory(directory.parent)
    except BaseException as error:
        if published:
            raise AmbiguousCommit(
                "Commit publication may have succeeded; explicit digest-bound readback is required",
                reference,
            ) from error
        raise
    return reference


def load_rank(
    path: Path | str,
    *,
    expected_binding: dict[str, Any],
    expected_manifest_digest: str,
    rank: int,
) -> LoadedRank:
    directory = safe_path(path)
    expected = validate_binding(expected_binding)
    require(
        type(expected_manifest_digest) is str
        and SHA.fullmatch(expected_manifest_digest) is not None,
        "Require an expected committed manifest digest",
    )
    marker = read_json(directory / "COMMITTED.json", allow_links=True)
    require(
        set(marker) == {"schema_version", "kind", "manifest_digest", "transaction_digest"}
        and type(marker["schema_version"]) is int
        and marker["schema_version"] == 1
        and marker["kind"] == COMMIT_KIND
        and marker["manifest_digest"] == expected_manifest_digest,
        "Missing, partial or mismatched checkpoint commit",
    )
    raw = read_bytes(directory / "manifest.json", MAX_JSON)
    require(sha(raw) == expected_manifest_digest, "Committed manifest hash differs")
    manifest = parse_json(raw)
    require(
        set(manifest)
        == {
            "schema_version",
            "kind",
            "transaction_digest",
            "binding",
            "progress",
            "ranks",
            "training_run_status",
        }
        and type(manifest["schema_version"]) is int
        and manifest["schema_version"] == 1
        and manifest["kind"] == "torch_training_checkpoint_manifest_v1"
        and manifest["training_run_status"] == "not_attested",
        "Unknown checkpoint manifest",
    )
    validate_progress(manifest["progress"])
    require(
        json_bytes(manifest["binding"]) == json_bytes(expected),
        "Source/program/runtime/data/parameter-group binding differs",
    )
    transaction = Transaction(str(directory), manifest["transaction_digest"])
    _, tx = read_transaction(transaction)
    require(
        marker["transaction_digest"] == transaction.transaction_digest
        and manifest["binding"] == tx["binding"]
        and manifest["progress"] == tx["progress"],
        "Manifest/transaction identity mismatch",
    )
    world = expected["world_size"]
    require(integer(rank, maximum=world - 1), "Invalid restore rank")
    require(
        type(manifest["ranks"]) is list and len(manifest["ranks"]) == world,
        "Incomplete rank commit",
    )
    acks = []
    for r, item in enumerate(manifest["ranks"]):
        require(
            type(item) is dict
            and set(item) == {"rank", "ready_digest", "replica_digest"}
            and item["rank"] == r
            and type(item["rank"]) is int,
            "Duplicate or reordered rank commit",
        )
        acks.append(RankAck(**item))
    total = 0
    selected_state = None
    for ack in acks:
        checked = verify_rank(
            directory,
            tx,
            transaction.transaction_digest,
            ack,
            remaining_bytes=MAX_TOTAL - total,
        )
        total += checked["bytes"]
        if ack.rank == rank:
            selected_state = checked["state"]
        del checked
    require(
        selected_state is not None and len({ack.replica_digest for ack in acks}) == 1,
        "Invalid complete replica state",
    )
    require(
        {p.name for p in directory.iterdir()}
        == {
            "transaction.json",
            "manifest.json",
            "COMMITTED.json",
            *[f"rank-{r:05d}" for r in range(world)],
        },
        "Unknown checkpoint files",
    )
    reference = CheckpointRef(
        str(directory), expected_manifest_digest, transaction.transaction_digest
    )
    assert isinstance(selected_state, dict)
    return LoadedRank(
        reference,
        expected,
        tx["progress"],
        tx["expected_ledgers"][rank],
        selected_state,
    )
