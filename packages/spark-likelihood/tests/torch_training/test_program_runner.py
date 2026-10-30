"""Pure contracts for the independent CPU executor training namespace."""

from __future__ import annotations

import sys

import pytest
from ds60_torch_training.contracts import TrainingError
from ds60_torch_training.program import TrainingProgram, ledger, schedule
from ds60_torch_training.runner import (
    RUNTIME_MODULES,
    _admit_runtime_identity,
    _rank_environment,
)
from ds60_torch_training.training_examples import linear_sgd_oracle, mlp_adam_example


@pytest.mark.parametrize("factory", [linear_sgd_oracle, mlp_adam_example])
def test_named_recipe_round_trip_without_torch_import(factory):
    before = "torch" in sys.modules
    descriptor = factory().descriptor()
    assert TrainingProgram.from_descriptor(descriptor).descriptor() == descriptor
    assert ("torch" in sys.modules) == before


def test_code_identity_rejects_changed_source_metadata():
    descriptor = linear_sgd_oracle().descriptor()
    descriptor["code_modules"]["ds60_torch_training.training_examples"] = "0" * 64
    with pytest.raises(TrainingError):
        TrainingProgram.from_descriptor(descriptor)


def test_fixed_schedule_covers_unequal_rank_rows_once():
    assignment = {
        "assignment_digest": "a" * 64,
        "ranks": [{"rank": 0, "rows": 4}, {"rank": 1, "rows": 2}],
    }
    result = schedule(assignment, epochs=2, steps_per_epoch=2, max_batch_rows=2, seed=4)
    assert result["ranks"] == [
        {"rank": 0, "ranges": [[0, 2], [2, 4]]},
        {"rank": 1, "ranges": [[0, 1], [1, 2]]},
    ]


def test_zero_or_missing_rank_environment_refused(monkeypatch):
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.setenv("RANK", "0")
    monkeypatch.setenv("WORLD_SIZE", "2")
    with pytest.raises(TrainingError):
        _rank_environment(2)
    monkeypatch.setenv("LOCAL_RANK", "0")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    with pytest.raises(TrainingError):
        _rank_environment(2)


def test_epoch_ledger_binds_order_and_weight():
    first = [
        {"id": 1, "features": [1.0], "label": 1.0, "weight": 3.0},
        {"id": 2, "features": [1.0], "label": 0.0, "weight": 1.0},
    ]
    one = ledger(first, 1)
    two = ledger(list(reversed(first)), 1)
    assert one["row_count"] == 2 and one["weight_sum"] == 4.0
    assert one["membership_digest"] != two["membership_digest"]
    assert one["data_digest"] != two["data_digest"]


@pytest.mark.parametrize("module", ["ds60_torch_training.launch", "ds60_torch_training.observer"])
def test_changed_critical_source_refused(module, monkeypatch):
    assert module in RUNTIME_MODULES
    actual = {"sources": dict.fromkeys(RUNTIME_MODULES, "a" * 64)}
    expected = {"sources": dict(actual["sources"])}
    expected["sources"][module] = "b" * 64
    monkeypatch.setattr("ds60_torch_training.runner.runtime_identity", lambda: actual)
    with pytest.raises(TrainingError, match="source identity differs"):
        _admit_runtime_identity(expected)
