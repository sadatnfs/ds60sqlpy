"""Population, temporal and lifecycle semantics for the ML engineering path."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/ml-engineering"


def reference(number: int) -> ModuleType:
    pytest.importorskip("numpy", reason="Prepared data runtime required")
    pytest.importorskip("pandas", reason="Prepared data runtime required")
    spec = importlib.util.spec_from_file_location(
        f"mle_course_{number}", BASE / "references" / f"mle-{number:03}_reference.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mle_subject_and_substantive_guides() -> None:
    track = json.loads((BASE / "track.json").read_text())
    admission = json.loads((BASE / "lessons.json").read_text())
    assert [row["id"] for row in track["lessons"]] == [f"mle-{n:03}" for n in range(1, 19)]
    assert len(admission["lessons"]) == 18
    for row in admission["lessons"]:
        assert row["runtime_profile"] == "data-engineering"
        assert row["verification_id"] is None
        for path in (row["guide_path"], row["source_path"], *row["solution_paths"]):
            assert (ROOT / path).is_file()
        guide = (ROOT / row["guide_path"]).read_text()
        assert guide.count("## Worked case ") == 2
        assert all(f"### {n}. " in guide for n in range(1, 7))
        assert len(re.sub(r"```.*?```", "", guide, flags=re.S).split()) >= 600
        assert "—" not in guide
    assert (BASE / "projects/local-system/.ds60-ml-project.json").is_file()


def test_mle_authoring_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_mle_label_availability_does_not_train_on_future_labels() -> None:
    module = reference(2)
    result = module.example_two()
    expected = [n for n in range(120) if n + 100 < 180 and n + 104 <= 180]
    assert result["mature_training_rows"] == len(expected) == 77
    assert result["not_yet_known_labels"] == [77, 78, 79]
    assert module.example_one()["eligible"] == [10, 30]


def test_mle_feast_preserves_requested_population_and_expiry() -> None:
    pytest.importorskip("feast", reason="Prepared Feast runtime required")
    module = reference(6)
    result = module.example_two()
    assert result["requested_rows"] == 3
    assert result["nulls_for_unknown_or_expired"] == 2
    assert module.example_one()["historical_usage"] == [10.0, 20.0, 5.0]


def test_mle_delayed_label_metric_has_fixed_cohort() -> None:
    result = reference(15).example_one()
    assert result["mature_prediction_ids"] == [1, 3]
    assert result["label_coverage"] == 2 / 4
    assert result["brier"] == pytest.approx(((0.1 - 0) ** 2 + (0.6 - 1) ** 2) / 2)


def test_mle_retry_invalidates_only_under_declared_identity() -> None:
    module = reference(13)
    original = module.example_one()
    changed = module.example_two()
    assert original["mean"] == sum([2, 4, 6]) / 3
    assert changed["new_mean"] == sum([2, 4, 8]) / 3
    assert changed["changed_input_invalidates_reuse"]


def test_mle_rejected_candidate_and_rollback_keep_accepted_version() -> None:
    module = reference(16)
    assert module.example_one()["failed_candidate_kept_active_v1"]
    assert module.example_two()["accepted_version"] == "v1"
