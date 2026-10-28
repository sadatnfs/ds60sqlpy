"""Reader delivery and independent contracts for the ML lifecycle contribution."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.lesson_reader import LinkResolver, render_markdown

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/data-ml-engineering/authoring/ml-lifecycle"


@pytest.mark.parametrize("number", range(33, 41))
def test_lifecycle_chapters_render_real_math_and_highlighted_complete_program(number: int) -> None:
    key = f"dme-{number:03}"
    source = BASE / "chapters" / (key + ".md")
    program = (BASE / "programs" / (key + ".py")).read_text()
    guide = source.read_text().replace("<!-- worked-program -->", "```python\n" + program + "```")
    rendered = render_markdown(
        guide, resolver=LinkResolver(repo_root=ROOT, source_path=source, targets={})
    )
    assert "<math" in rendered
    assert "math-source" not in rendered
    assert 'class="language-python"' in rendered
    assert "Worked case 1" in rendered and "Worked case 2" in rendered


@pytest.fixture
def numerical_loader() -> dict[str, Any]:
    pytest.importorskip("numpy", reason="Numerical artifact code uses prepared NumPy")
    return runpy.run_path(str(BASE / "programs/dme-040.py"))


def payload() -> dict[str, Any]:
    return {
        "format_version": 1,
        "feature_names": ["hours", "tickets"],
        "feature_units": {"hours": "hours", "tickets": "count"},
        "intercept": 3.0,
        "coefficients": [2.0, -1.5],
    }


@pytest.mark.parametrize("layer", ["manifest", "model"])
def test_boolean_versions_cannot_masquerade_as_integer_version_one(
    layer: str, tmp_path: Path, numerical_loader: dict[str, Any]
) -> None:
    directory = tmp_path / "owned-version"
    model = payload()
    if layer == "model":
        model["format_version"] = True
    manifest = numerical_loader["publish_bundle"](directory, model)
    if layer == "manifest":
        manifest["schema_version"] = True
        (directory / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="version|format"):
        numerical_loader["load_bundle"](directory)


@pytest.mark.parametrize("coefficient", [True, "2.0", 10**400])
def test_matching_hash_does_not_bypass_parameter_type_and_numeric_bounds(
    coefficient: Any, tmp_path: Path, numerical_loader: dict[str, Any]
) -> None:
    directory = tmp_path / "owned-version"
    model = {**payload(), "coefficients": [coefficient, -1.5]}
    numerical_loader["publish_bundle"](directory, model)
    # In particular, a huge integer must produce the controlled contract error,
    # rather than escaping as math.isfinite's floating-conversion OverflowError.
    with pytest.raises(ValueError, match="finite bounded numerical"):
        numerical_loader["load_bundle"](directory)


def test_bound_applies_to_actual_file_bytes(
    tmp_path: Path, numerical_loader: dict[str, Any]
) -> None:
    path = tmp_path / "oversized.bin"
    path.write_bytes(b"x" * (numerical_loader["MAX_BYTES"] + 1))
    with pytest.raises(ValueError, match="bounded regular|budget"):
        numerical_loader["bounded_read"](path)
