"""Local artifact failures must occur before loading a pretrained model."""

from __future__ import annotations

import ast
import hashlib
import json
import runpy
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "courses/llm-applied/fixtures/pretrained"


@pytest.fixture
def assets(tmp_path: Path) -> Path:
    weights = b"fixture bytes only; no actual model"
    (tmp_path / "model.safetensors").write_bytes(weights)
    metadata = json.loads((RECIPE / "asset_contract.json").read_text())
    metadata["files"] = {"model.safetensors": hashlib.sha256(weights).hexdigest()}
    (tmp_path / "course-assets.json").write_text(json.dumps(metadata))
    return tmp_path


def verify(path: Path) -> dict[str, Any]:
    function = runpy.run_path(str(RECIPE / "verify_assets.py"))["verify_assets"]
    result = function(path)
    assert isinstance(result, dict)
    return result


def test_unlisted_configuration_cannot_change_verified_model_loading(assets: Path) -> None:
    assert verify(assets)["files"]
    (assets / "config.json").write_text('{"model_type":"changed"}')
    with pytest.raises(ValueError, match="Unlisted"):
        verify(assets)


def test_nested_manifest_named_file_is_not_an_inventory_exception(assets: Path) -> None:
    (assets / "nested").mkdir()
    (assets / "nested/course-assets.json").write_text("{}")
    with pytest.raises(ValueError, match="Unlisted"):
        verify(assets)


def test_snapshot_identity_mismatch_is_rejected_before_hashes(assets: Path) -> None:
    path = assets / "course-assets.json"
    metadata = json.loads(path.read_text())
    metadata["revision"] = "different-snapshot"
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="identity mismatch"):
        verify(assets)


def test_symlink_parent_cannot_redirect_a_hashed_asset(assets: Path) -> None:
    folder = assets / "actual"
    folder.mkdir()
    (folder / "extra.json").write_text("{}")
    try:
        (assets / "alias").symlink_to(folder, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("This OS does not permit creating a test directory symlink")
    path = assets / "course-assets.json"
    metadata = json.loads(path.read_text())
    metadata["files"]["alias/extra.json"] = hashlib.sha256(b"{}").hexdigest()
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="Unsafe asset path"):
        verify(assets)


def test_adapter_initialization_is_seeded_before_model_and_trainer_construction() -> None:
    tree = ast.parse((RECIPE / "train_local.py").read_text())
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    seed = next(
        node for node in calls if isinstance(node.func, ast.Name) and node.func.id == "set_seed"
    )
    assert isinstance(seed.args[0], ast.Constant) and seed.args[0].value == 7
    constructors = [
        node
        for node in calls
        if isinstance(node.func, ast.Name)
        and node.func.id == "SFTTrainer"
        or isinstance(node.func, ast.Attribute)
        and node.func.attr == "from_pretrained"
    ]
    assert constructors and all(seed.lineno < node.lineno for node in constructors)
