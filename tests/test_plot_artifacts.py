"""Plot receipts stay bounded and contain data, not executable page fragments."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.plot_artifacts import read_artifacts, validate_artifacts


def chart() -> dict[str, Any]:
    return {
        "kind": "plotly",
        "figure": {
            "data": [{"type": "scatter", "x": [1, 2], "y": [3, 5]}],
            "layout": {
                "meta": {
                    "description": "Observed values",
                    "table": {"columns": ["x", "y"], "rows": [[1, 3], [2, 5]]},
                }
            },
        },
    }


def test_validate_chart_carries_accessible_table_and_finite_values() -> None:
    result = validate_artifacts([chart()])
    assert result[0]["description"] == "Observed values"
    assert result[0]["table"]["rows"] == [[1, 3], [2, 5]]
    assert "html" not in result[0]


@pytest.mark.parametrize("change", ["code", "nan", "type", "oversized", "table", "image", "many"])
def test_chart_contract_rejects_invalid_or_unbounded_data(change: str) -> None:
    artifact = copy.deepcopy(chart())
    if change == "code":
        artifact["figure"]["script"] = "alert(1)"
    elif change == "nan":
        artifact["figure"]["data"][0]["y"] = [float("nan")]
    elif change == "type":
        artifact["figure"]["data"][0]["type"] = "scattermap"
    elif change == "oversized":
        artifact["figure"]["layout"]["title"] = "x" * 180001
    elif change == "table":
        artifact["figure"]["layout"]["meta"]["table"]["rows"] = [[1]]
    elif change == "image":
        artifact["figure"]["layout"]["images"] = [{"source": "https://example.com/image.png"}]
    with pytest.raises(ValueError):
        validate_artifacts([artifact] * (3 if change == "many" else 1))


def test_untrusted_figure_file_cannot_follow_link(tmp_path: Path) -> None:
    other = tmp_path / "other.json"
    other.write_text(json.dumps([chart()]))
    (tmp_path / "ds60-figures.json").symlink_to(other)
    artifacts, warning = read_artifacts(tmp_path)
    assert not artifacts and "could not be saved" in warning


def test_new_figure_file_is_read_without_running_anything(tmp_path: Path) -> None:
    (tmp_path / "ds60-figures.json").write_text(json.dumps([chart()]))
    artifacts, warning = read_artifacts(tmp_path)
    assert not warning and artifacts[0]["kind"] == "plotly"


@pytest.mark.parametrize(
    "frame",
    [
        {"data": [{"type": "scattermapbox"}]},
        {"layout": {"images": [{"source": "https://example.invalid/image.png"}]}},
        {"data": [{"source": "https://example.invalid/image.png"}]},
    ],
)
def test_animation_frames_have_the_same_offline_contract(frame: dict[str, Any]) -> None:
    value = chart()
    value["figure"]["frames"] = [frame]
    with pytest.raises(ValueError):
        validate_artifacts([value])


def test_image_trace_cannot_fetch_external_bytes() -> None:
    value = chart()
    value["figure"]["data"] = [{"type": "image", "source": "https://example.invalid/image.png"}]
    with pytest.raises(ValueError, match="image sources"):
        validate_artifacts([value])


def test_all_fixed_python_startup_probes_are_valid_programs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ds60sqlpy import worker_operations as operations

    seen: list[str] = []
    monkeypatch.setattr(importlib.util, "find_spec", lambda module: object())

    def parse_command(command: list[str], *args: object, **kwargs: object) -> tuple[int, None]:
        assert command[1] == "-c"
        compile(command[2], "<fixed-probe>", "exec")
        seen.append(command[2])
        return 0, None

    monkeypatch.setattr(operations, "run_process", parse_command)
    for profile in ("python-core", "tensorflow-cpu", "llm-torch-cpu", "jax-cpu", "bayesian-cpu"):
        assert operations.probe_profile(profile)[0]
    assert len(seen) == 5 and "with m.Model():" in seen[-1]
