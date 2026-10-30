"""Prepared Torch 2.9.1+cpu continuation on native Linux ARM64 or AMD64.

This tests model, optimizer and RNG restoration. Spark placement and actual
worker-loss recovery have separate integration gates.
"""

from __future__ import annotations

import hashlib
import random
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    import torch
except ImportError as error:
    raise unittest.SkipTest("Real Torch and NumPy are required") from error

from ds60_torch_training import checkpoint as cp
from ds60_torch_training import torch_adapter as adapter


def _model():
    return torch.nn.Sequential(
        torch.nn.Linear(2, 3, dtype=torch.float64),
        torch.nn.Dropout(0.2),
        torch.nn.Linear(3, 1, dtype=torch.float64),
    )


def _optimizer(model, kind):
    options = {"lr": 0.01, "momentum": 0.9} if kind == "SGD" else {"lr": 0.01}
    return getattr(torch.optim, kind)(model.parameters(), **options)


def _binding(model, optimizer, loss):
    schema = adapter.module_schema_digest(model)
    digests = {field: hashlib.sha256(field.encode()).hexdigest() for field in cp.DIGEST_FIELDS}
    digests["definition_digest"] = cp.digest_value(
        {"program": "runtime-continuation-v1", "module_schema_digest": schema}
    )
    digests["loss_state_digest"] = adapter.loss_state_digest(loss)
    return {
        "schema_version": 1,
        "kind": cp.BINDING_KIND,
        **digests,
        "world_size": 1,
        "model_layout": adapter.model_layout(model),
        "optimizer_layout": adapter.optimizer_layout(model, optimizer),
    }


def _steps(model, optimizer, loss, count):
    x = torch.tensor([[0.2, -0.1], [0.4, 0.3]], dtype=torch.float64)
    y = torch.tensor([[0.5], [-0.2]], dtype=torch.float64)
    for _ in range(count):
        optimizer.zero_grad(set_to_none=True)
        error = loss(model(x), y)
        error.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)


def _check_real_torch_checkpoint_resume_matches_uninterrupted_cpu(tmp_path, kind):
    assert torch.__version__.startswith("2.9.1")
    assert torch.device("cpu").type == "cpu"
    torch.set_num_threads(1)
    random.seed(1729)
    np.random.seed(1729)
    torch.manual_seed(1729)
    model = _model()
    optimizer = _optimizer(model, kind)
    loss = torch.nn.MSELoss()
    expected_schema = adapter.module_schema_digest(model)
    binding = _binding(model, optimizer, loss)
    progress = {
        "boundary": "completed_epoch",
        "epoch": 0,
        "global_step": 2,
        "epoch_steps": 2,
    }
    ledger = {
        "row_count": 2,
        "weight_sum": 2.0,
        "membership_digest": hashlib.sha256(b"rows").hexdigest(),
        "data_digest": hashlib.sha256(b"values").hexdigest(),
        "steps": 2,
    }
    sampler = {
        "kind": "fixed_order_v1",
        "seed": None,
        "next_epoch": 1,
        "cursor": 0,
        "generator_names": [],
    }
    _steps(model, optimizer, loss, 2)
    captured = adapter.capture_rank_state(
        model,
        optimizer,
        loss,
        expected_binding=binding,
        expected_module_schema_digest=expected_schema,
        progress=progress,
        sampler=sampler,
    )
    transaction = cp.begin_checkpoint(
        tmp_path,
        "epoch-000",
        binding,
        progress,
        [ledger],
        run_id="runtime-test",
        attempt_id="original",
    )
    ack = cp.write_rank(transaction, 0, captured, ledger=ledger)
    reference = cp.commit_checkpoint(transaction, [ack])
    loaded = cp.load_rank(
        reference.path,
        expected_binding=binding,
        expected_manifest_digest=reference.manifest_digest,
        rank=0,
    )
    _steps(model, optimizer, loss, 2)
    expected_weights = [item.detach().clone() for item in model.parameters()]
    expected_rng = (random.random(), float(np.random.random()), float(torch.rand(())))

    resumed_model = _model()
    resumed_optimizer = _optimizer(resumed_model, kind)
    resumed_loss = torch.nn.MSELoss()
    adapter.restore_rank_state(
        resumed_model,
        resumed_optimizer,
        resumed_loss,
        loaded,
        expected_binding=binding,
        expected_module_schema_digest=expected_schema,
    )
    _steps(resumed_model, resumed_optimizer, resumed_loss, 2)
    actual_weights = [item.detach() for item in resumed_model.parameters()]
    assert all(torch.equal(a, b) for a, b in zip(actual_weights, expected_weights, strict=True))
    assert (
        random.random(),
        float(np.random.random()),
        float(torch.rand(())),
    ) == expected_rng


@unittest.skipUnless(
    str(torch.__version__).startswith("2.9.1+cpu"),
    "requires the prepared Torch 2.9.1+cpu runtime",
)
class RuntimeCheckpointTests(unittest.TestCase):
    def test_real_torch_checkpoint_resume(self):
        for kind in ("SGD", "Adam", "AdamW"):
            with (
                self.subTest(optimizer=kind),
                tempfile.TemporaryDirectory() as directory,
            ):
                _check_real_torch_checkpoint_resume_matches_uninterrupted_cpu(Path(directory), kind)


if __name__ == "__main__":
    unittest.main()
