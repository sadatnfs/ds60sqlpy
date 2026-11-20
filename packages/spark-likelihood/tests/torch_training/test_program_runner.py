"""Pure contracts for the independent CPU executor training namespace."""

from __future__ import annotations

import faulthandler
import json
import signal
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from ds60_torch_training.contracts import TrainingError
from ds60_torch_training.program import TrainingProgram, ledger, schedule
from ds60_torch_training.runner import (
    RUNTIME_MODULES,
    _admit_runtime_identity,
    _rank_environment,
    _RankDiagnostics,
)
from ds60_torch_training.training_examples import linear_sgd_oracle, mlp_adam_example

SOURCE = Path(__file__).resolve().parents[2] / "src"


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


def _diagnosed_rank(output: Path, body: str) -> subprocess.CompletedProcess:
    """Run a rank stand-in in a child so faulthandler state stays out of pytest."""
    code = (
        "import os, signal, sys, time\n"
        f"sys.path.insert(0, {str(SOURCE)!r})\n"
        "from ds60_torch_training import runner\n"
        "runner.MIN_STACK_INTERVAL_SECONDS = 0.1\n"
        "runner.EXIT_GRACE_SECONDS = 0.2\n"
        f"plan = {{'output_dir': {str(output)!r}, 'run_id': 'r', 'timeout_seconds': 0.1}}\n"
        "diagnostics = runner._RankDiagnostics.start(plan, 1)\n" + textwrap.dedent(body)
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=60
    )


def _diagnostic_files(output: Path) -> tuple[list[dict], str]:
    (progress,) = (output / "diagnostics").glob("rank-00001-pid-*.progress.jsonl")
    stacks = progress.with_name(progress.name.replace(".progress.jsonl", ".stacks.txt"))
    events = [json.loads(line) for line in progress.read_text().splitlines()]
    return events, stacks.read_text()


def test_stalled_rank_leaves_progress_and_stacks_before_and_after_return(tmp_path):
    result = _diagnosed_rank(
        tmp_path,
        """
        def stalled_collective():
            time.sleep(1.0)
        def stalled_exit():
            time.sleep(1.5)
        with diagnostics.phase("gather_receipts", epoch=0):
            stalled_collective()
        diagnostics.finish(None)
        stalled_exit()
        """,
    )
    assert result.returncode == 0, result.stderr
    events, stacks = _diagnostic_files(tmp_path)
    assert [(item["event"], item.get("edge")) for item in events] == [
        ("start", None),
        ("gather_receipts", "begin"),
        ("gather_receipts", "end"),
        ("return", None),
        ("interpreter_exit", None),
    ]
    assert events[0]["rank"] == 1 and events[0]["stack_interval_seconds"] == 0.1
    assert "in stalled_collective" in stacks and "in stalled_exit" in stacks


@pytest.mark.skipif(not hasattr(faulthandler, "register"), reason="POSIX signal chaining")
def test_terminated_rank_dumps_stacks_and_still_dies_by_sigterm(tmp_path):
    result = _diagnosed_rank(
        tmp_path,
        """
        def cancelled_rank():
            os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(5)
        cancelled_rank()
        """,
    )
    assert result.returncode == -signal.SIGTERM
    events, stacks = _diagnostic_files(tmp_path)
    assert [item["event"] for item in events] == ["start"]
    assert "in cancelled_rank" in stacks


def test_unwritable_diagnostics_never_block_training(tmp_path):
    output = tmp_path / "not-a-directory"
    output.write_text("")
    diagnostics = _RankDiagnostics.start(
        {"output_dir": str(output), "run_id": "r", "timeout_seconds": 1.0}, 0
    )
    with diagnostics.phase("gather_receipts"):
        diagnostics.step(epoch=0, global_step=0)
    diagnostics.finish(RuntimeError("rank failed"))
    assert list(tmp_path.iterdir()) == [output]
