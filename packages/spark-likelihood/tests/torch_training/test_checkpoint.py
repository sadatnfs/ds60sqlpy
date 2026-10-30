"""Pure checkpoint safety tests. No Torch, Spark or numerical training executes."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import random
import struct
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "src/ds60_torch_training/checkpoint.py"
SPEC = importlib.util.spec_from_file_location("work_checkpoint", MODULE)
assert SPEC is not None and SPEC.loader is not None
cp = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cp
SPEC.loader.exec_module(cp)


def tensor(values, dtype="float64", shape=None):
    shape = (len(values),) if shape is None else shape
    return cp.TensorData(
        dtype, shape, struct.pack("<" + cp.DTYPES[dtype][1] * len(values), *values)
    )


def binding(world=2, optimizer="torch.optim.SGD"):
    options = {
        "lr": 0.1,
        "weight_decay": 0.0,
        "momentum": 0.9,
        "dampening": 0.0,
        "nesterov": False,
    }
    if not optimizer.endswith("SGD"):
        options = {
            "lr": 0.01,
            "weight_decay": 0.0,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "amsgrad": False,
            "decoupled_weight_decay": optimizer.endswith("AdamW"),
        }
    return {
        "schema_version": 1,
        "kind": cp.BINDING_KIND,
        **{field: hashlib.sha256(field.encode()).hexdigest() for field in cp.DIGEST_FIELDS},
        "world_size": world,
        "model_layout": [
            {
                "name": "weight",
                "role": "parameter",
                "dtype": "float64",
                "shape": [2],
                "requires_grad": True,
            },
            {
                "name": "bias",
                "role": "parameter",
                "dtype": "float64",
                "shape": [2],
                "requires_grad": True,
            },
            {
                "name": "count",
                "role": "buffer",
                "dtype": "int64",
                "shape": [],
                "requires_grad": False,
            },
        ],
        "optimizer_layout": {
            "class": optimizer,
            "groups": [{"names": ["weight", "bias"], "options": options}],
        },
    }


PROGRESS = {
    "boundary": "completed_epoch",
    "epoch": 0,
    "global_step": 2,
    "epoch_steps": 2,
}


def ledger(rank):
    return {
        "row_count": 4 if rank == 0 else 2,
        "weight_sum": 4.0 if rank == 0 else 2.0,
        "membership_digest": hashlib.sha256(f"ids-{rank}".encode()).hexdigest(),
        "data_digest": hashlib.sha256(f"data-{rank}".encode()).hexdigest(),
        "steps": 2,
    }


def state(rank=0, optimizer="torch.optim.SGD"):
    optimizer_state = {name: {"momentum_buffer": tensor([0.1, 0.2])} for name in ["weight", "bias"]}
    if not optimizer.endswith("SGD"):
        optimizer_state = {
            name: {
                "step": tensor([2.0], "float32", ()),
                "exp_avg": tensor([0.1, 0.2]),
                "exp_avg_sq": tensor([0.01, 0.02]),
            }
            for name in ["weight", "bias"]
        }
    return {
        "model": {
            "weight": tensor([0.2, 0.4]),
            "bias": tensor([0.0, 0.1]),
            "count": tensor([rank], "int64", ()),
        },
        "optimizer": optimizer_state,
        "rng": {
            "python": random.Random(1729 + rank).getstate(),
            "numpy": ("MT19937", tensor(list(range(624)), "uint32"), 3, 0, 0.0),
            "torch_cpu": cp.TensorData("uint8", (16,), bytes(range(rank, rank + 16))),
            "generators": {},
        },
        "sampler": {
            "kind": "fixed_order_v1",
            "seed": None,
            "next_epoch": 1,
            "cursor": 0,
            "generator_names": [],
        },
        "module_modes": {"": True, "dropout": True},
        "loss_state_digest": binding()["loss_state_digest"],
    }


def prepared(tmp_path, *, optimizer="torch.optim.SGD"):
    root = tmp_path.resolve()
    b = binding(optimizer=optimizer)
    transaction = cp.begin_checkpoint(
        root,
        "epoch-000",
        b,
        PROGRESS,
        [ledger(0), ledger(1)],
        run_id="run-a",
        attempt_id="attempt-1",
    )
    acks = [
        cp.write_rank(transaction, rank, state(rank, optimizer), ledger=ledger(rank))
        for rank in range(2)
    ]
    return b, transaction, acks


def reseal(root, rank):
    rank_dir = root / f"rank-{rank:05d}"
    ready = json.loads((rank_dir / "READY.json").read_text())
    ready_raw = cp.json_bytes(ready)
    (rank_dir / "READY.json").write_bytes(ready_raw)
    manifest = json.loads((root / "manifest.json").read_text())
    manifest["ranks"][rank]["ready_digest"] = cp.sha(ready_raw)
    manifest_raw = cp.json_bytes(manifest)
    (root / "manifest.json").write_bytes(manifest_raw)
    marker = json.loads((root / "COMMITTED.json").read_text())
    marker["manifest_digest"] = cp.sha(manifest_raw)
    (root / "COMMITTED.json").write_bytes(cp.json_bytes(marker))
    return marker["manifest_digest"]


@pytest.mark.parametrize("optimizer", ["torch.optim.SGD", "torch.optim.Adam", "torch.optim.AdamW"])
def test_round_trip_named_state_buffers_rng_and_progress(tmp_path, optimizer):
    b, transaction, acks = prepared(tmp_path, optimizer=optimizer)
    reference = cp.commit_checkpoint(transaction, acks)
    assert reference.training_run_status == "not_attested"
    for rank in range(2):
        loaded = cp.load_rank(
            reference.path,
            expected_binding=b,
            expected_manifest_digest=reference.manifest_digest,
            rank=rank,
        )
        assert loaded.state == state(rank, optimizer)
        assert loaded.progress == PROGRESS and loaded.ledger == ledger(rank)
        expected_random = random.Random()
        expected_random.setstate(state(rank)["rng"]["python"])
        actual_random = random.Random()
        actual_random.setstate(loaded.state["rng"]["python"])
        assert actual_random.random() == expected_random.random()
    assert not list(tmp_path.rglob("*.pt")) and not list(tmp_path.rglob("*.pkl"))


@pytest.mark.parametrize("field", sorted(cp.DIGEST_FIELDS) + ["world_size"])
def test_changed_source_data_schedule_or_world_is_rejected(tmp_path, field):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    changed = copy.deepcopy(b)
    changed[field] = 1 if field == "world_size" else "f" * 64
    with pytest.raises(cp.CheckpointError, match="binding differs"):
        cp.load_rank(
            Path(reference.path),
            expected_binding=changed,
            expected_manifest_digest=reference.manifest_digest,
            rank=0,
        )


def test_same_shape_parameter_group_swap_is_rejected(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    b["optimizer_layout"]["groups"][0]["names"] = ["bias", "weight"]
    with pytest.raises(cp.CheckpointError, match="binding differs"):
        cp.load_rank(
            Path(reference.path),
            expected_binding=b,
            expected_manifest_digest=reference.manifest_digest,
            rank=0,
        )


def test_partial_checkpoint_and_missing_rank_never_commit(tmp_path):
    b = binding()
    transaction = cp.begin_checkpoint(
        tmp_path.resolve(),
        "partial",
        b,
        PROGRESS,
        [ledger(0), ledger(1)],
        run_id="r",
        attempt_id="a",
    )
    ack = cp.write_rank(transaction, 0, state(), ledger=ledger(0))
    with pytest.raises(cp.CheckpointError, match="Every logical rank"):
        cp.commit_checkpoint(transaction, [ack])
    assert not (Path(transaction.path) / "COMMITTED.json").exists()
    with pytest.raises((cp.CheckpointError, OSError)):
        cp.load_rank(
            Path(transaction.path),
            expected_binding=b,
            expected_manifest_digest="0" * 64,
            rank=0,
        )


def test_rank_state_and_commits_are_append_only(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    with pytest.raises((cp.CheckpointError, FileExistsError)):
        cp.write_rank(transaction, 0, state(), ledger=ledger(0))
    reference = cp.commit_checkpoint(transaction, acks)
    before = (Path(reference.path) / "manifest.json").read_bytes()
    with pytest.raises(cp.CheckpointError, match="reconciled"):
        cp.commit_checkpoint(transaction, acks)
    with pytest.raises(cp.CheckpointError, match="append-only"):
        cp.begin_checkpoint(
            tmp_path.resolve(),
            "epoch-000",
            b,
            PROGRESS,
            [ledger(0), ledger(1)],
            run_id="r",
            attempt_id="a",
        )
    assert (Path(reference.path) / "manifest.json").read_bytes() == before


def test_data_delivery_drift_refuses_rank_before_creating_files(tmp_path):
    transaction = cp.begin_checkpoint(
        tmp_path.resolve(),
        "data",
        binding(),
        PROGRESS,
        [ledger(0), ledger(1)],
        run_id="r",
        attempt_id="a",
    )
    changed = ledger(0)
    changed["row_count"] += 1
    with pytest.raises(cp.CheckpointError, match="data ledger differs"):
        cp.write_rank(transaction, 0, state(), ledger=changed)
    assert not (Path(transaction.path) / "rank-00000").exists()


def test_zero_rank_weight_is_allowed_but_global_zero_is_rejected(tmp_path):
    rows = [ledger(0), ledger(1)]
    rows[0]["weight_sum"] = 0.0
    transaction = cp.begin_checkpoint(
        tmp_path.resolve(),
        "zero-rank",
        binding(),
        PROGRESS,
        rows,
        run_id="r",
        attempt_id="a",
    )
    cp.write_rank(transaction, 0, state(), ledger=rows[0])
    rows[1]["weight_sum"] = 0.0
    with pytest.raises(cp.CheckpointError, match="Global epoch weight"):
        cp.begin_checkpoint(
            tmp_path.resolve(),
            "zero-all",
            binding(),
            PROGRESS,
            rows,
            run_id="r",
            attempt_id="a",
        )


def test_disagreeing_parameter_replicas_refuse_commit(tmp_path):
    b, _, _ = prepared(tmp_path)
    # Build a fresh pair with a genuinely different second parameter replica.
    other = cp.begin_checkpoint(
        tmp_path.resolve(),
        "different",
        b,
        PROGRESS,
        [ledger(0), ledger(1)],
        run_id="r",
        attempt_id="a",
    )
    changed = state(1)
    changed["model"]["weight"] = tensor([1.0, 2.0])
    actual = [
        cp.write_rank(other, 0, state(), ledger=ledger(0)),
        cp.write_rank(other, 1, changed, ledger=ledger(1)),
    ]
    with pytest.raises(cp.CheckpointError, match="replicas disagree"):
        cp.commit_checkpoint(other, actual)
    assert not (Path(other.path) / "COMMITTED.json").exists()


@pytest.mark.parametrize(
    "mutation", ["shape", "nonfinite", "optimizer", "rng", "cursor", "loss", "custom"]
)
def test_unsupported_or_inconsistent_state_is_refused_before_rank_write(tmp_path, mutation):
    transaction = cp.begin_checkpoint(
        tmp_path.resolve(),
        "bad",
        binding(),
        PROGRESS,
        [ledger(0), ledger(1)],
        run_id="r",
        attempt_id="a",
    )
    changed = state()
    if mutation == "shape":
        changed["model"]["weight"] = tensor([1.0, 2.0], shape=(1, 2))
    elif mutation == "nonfinite":
        changed["model"]["weight"] = tensor([float("nan"), 2.0])
    elif mutation == "optimizer":
        changed["optimizer"]["weight"]["arbitrary"] = 1
    elif mutation == "rng":
        del changed["rng"]["numpy"]
    elif mutation == "cursor":
        changed["sampler"]["cursor"] = 1
    elif mutation == "loss":
        changed["loss_state_digest"] = "0" * 64
    else:
        changed["optimizer"]["weight"]["momentum_buffer"] = object()
    with pytest.raises(cp.CheckpointError):
        cp.write_rank(transaction, 0, changed, ledger=ledger(0))
    assert not (Path(transaction.path) / "rank-00000").exists()


def test_custom_reduce_is_never_called(tmp_path):
    marker = tmp_path / "executed"

    class Executable:
        def __reduce__(self):
            marker.write_text("unsafe")
            return (str, ("unsafe",))

    with pytest.raises(cp.CheckpointError, match="custom"):
        cp.encode_state({"value": Executable()})
    assert not marker.exists()


def test_tensor_hash_tampering_is_rejected(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    (Path(reference.path) / "rank-00000/tensor-00000.bin").write_bytes(b"x" * 16)
    with pytest.raises(cp.CheckpointError, match="hash"):
        cp.load_rank(
            Path(reference.path),
            expected_binding=b,
            expected_manifest_digest=reference.manifest_digest,
            rank=0,
        )


def test_forged_same_size_shape_is_rejected_against_trusted_layout(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    root = Path(reference.path)
    ready = cp.read_json(root / "rank-00000/READY.json")
    ready["tensors"][0]["shape"] = [1, 2]
    (root / "rank-00000/READY.json").write_bytes(cp.json_bytes(ready))
    expected = reseal(root, 0)
    with pytest.raises(cp.CheckpointError, match="layout differs"):
        cp.load_rank(root, expected_binding=b, expected_manifest_digest=expected, rank=0)


def test_unsafe_tensor_path_cannot_escape_even_with_forged_manifest_hash(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    root = Path(reference.path)
    ready = cp.read_json(root / "rank-00000/READY.json")
    ready["tensors"][0]["path"] = "../../escape"
    (root / "rank-00000/READY.json").write_bytes(cp.json_bytes(ready))
    expected = reseal(root, 0)
    with pytest.raises(cp.CheckpointError, match="Unsafe"):
        cp.load_rank(root, expected_binding=b, expected_manifest_digest=expected, rank=0)


def test_symlink_components_and_payloads_are_rejected(tmp_path):
    root = tmp_path.resolve()
    alias = root / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(cp.CheckpointError, match="Symlink"):
        cp.begin_checkpoint(
            alias,
            "bad",
            binding(),
            PROGRESS,
            [ledger(0), ledger(1)],
            run_id="r",
            attempt_id="a",
        )
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    target = Path(reference.path) / "rank-00000/tensor-00000.bin"
    target.unlink()
    target.symlink_to(root / "outside")
    with pytest.raises(cp.CheckpointError, match="Symlink"):
        cp.load_rank(
            Path(reference.path),
            expected_binding=b,
            expected_manifest_digest=reference.manifest_digest,
            rank=0,
        )


def test_duplicate_json_and_extra_payload_files_are_rejected(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"one":1,"one":2}')
    with pytest.raises(cp.CheckpointError, match="Duplicate"):
        cp.read_json(path)
    _, transaction, acks = prepared(tmp_path)
    (Path(transaction.path) / "rank-00000/extra.py").write_text(
        "raise RuntimeError('not executed')"
    )
    with pytest.raises(cp.CheckpointError, match="Unknown"):
        cp.commit_checkpoint(transaction, acks)


def test_global_byte_budget_is_checked_before_loading_next_rank(tmp_path, monkeypatch):
    _, transaction, acks = prepared(tmp_path)
    monkeypatch.setattr(cp, "MAX_TOTAL", 128)
    with pytest.raises(cp.CheckpointError, match="byte bound"):
        cp.commit_checkpoint(transaction, acks)
    assert not (Path(transaction.path) / "COMMITTED.json").exists()


def test_mutation_between_validation_and_publication_is_detected(tmp_path, monkeypatch):
    _, transaction, acks = prepared(tmp_path)
    original = cp.write_new

    def mutate(path, raw):
        original(path, raw)
        if path.name == "manifest.json":
            (Path(transaction.path) / "rank-00000/tensor-00000.bin").write_bytes(b"x" * 16)

    monkeypatch.setattr(cp, "write_new", mutate)
    with pytest.raises(cp.CheckpointError, match="hash"):
        cp.commit_checkpoint(transaction, acks)
    assert not (Path(transaction.path) / "COMMITTED.json").exists()


def test_post_publish_failure_is_ambiguous_and_requires_explicit_readback(tmp_path, monkeypatch):
    b, transaction, acks = prepared(tmp_path)
    original = cp.sync_directory

    def fail_after_publish(path):
        if path == Path(transaction.path) and (path / "COMMITTED.json").exists():
            raise OSError("injected durability acknowledgment failure")
        original(path)

    monkeypatch.setattr(cp, "sync_directory", fail_after_publish)
    with pytest.raises(cp.AmbiguousCommit) as failure:
        cp.commit_checkpoint(transaction, acks)
    reference = failure.value.reference
    loaded = cp.load_rank(
        Path(reference.path),
        expected_binding=b,
        expected_manifest_digest=reference.manifest_digest,
        rank=0,
    )
    assert loaded.reference.training_run_status == "not_attested"
    with pytest.raises(cp.CheckpointError, match="reconciled"):
        cp.commit_checkpoint(transaction, acks)


def test_manifest_boolean_epoch_is_not_an_integer_identity(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    root = Path(reference.path)
    manifest = cp.read_json(root / "manifest.json")
    manifest["progress"]["epoch"] = False
    raw = cp.json_bytes(manifest)
    (root / "manifest.json").write_bytes(raw)
    marker = cp.read_json(root / "COMMITTED.json")
    marker["manifest_digest"] = cp.sha(raw)
    (root / "COMMITTED.json").write_bytes(cp.json_bytes(marker))
    with pytest.raises(cp.CheckpointError, match="epoch boundary"):
        cp.load_rank(root, expected_binding=b, expected_manifest_digest=cp.sha(raw), rank=0)


def test_ready_boolean_epoch_is_rejected_even_with_resealed_manifest(tmp_path):
    b, transaction, acks = prepared(tmp_path)
    reference = cp.commit_checkpoint(transaction, acks)
    root = Path(reference.path)
    ready = cp.read_json(root / "rank-00000/READY.json")
    ready["progress"]["epoch"] = False
    (root / "rank-00000/READY.json").write_bytes(cp.json_bytes(ready))
    digest = reseal(root, 0)
    with pytest.raises(cp.CheckpointError, match="epoch boundary"):
        cp.load_rank(root, expected_binding=b, expected_manifest_digest=digest, rank=0)


def test_post_publication_payload_mutation_never_returns_success(tmp_path, monkeypatch):
    b, transaction, acks = prepared(tmp_path)
    original = cp.os.link

    def corrupt_after_link(source, destination, **kwargs):
        original(source, destination, **kwargs)
        (Path(transaction.path) / "rank-00000/tensor-00000.bin").write_bytes(b"x" * 16)

    monkeypatch.setattr(cp.os, "link", corrupt_after_link)
    with pytest.raises(cp.AmbiguousCommit) as failure:
        cp.commit_checkpoint(transaction, acks)
    with pytest.raises(cp.CheckpointError, match="hash"):
        cp.load_rank(
            Path(transaction.path),
            expected_binding=b,
            expected_manifest_digest=failure.value.reference.manifest_digest,
            rank=0,
        )


def test_actual_file_read_bound_does_not_trust_stale_stat(tmp_path, monkeypatch):
    import types

    path = tmp_path / "bounded.bin"
    path.write_bytes(b"sixxxx")
    original = cp.os.fstat

    def stale(descriptor):
        value = original(descriptor)
        return types.SimpleNamespace(st_mode=value.st_mode, st_nlink=value.st_nlink, st_size=0)

    monkeypatch.setattr(cp.os, "fstat", stale)
    with pytest.raises(cp.CheckpointError, match="actual read bound"):
        cp.read_bytes(path, 5)
