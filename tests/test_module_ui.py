"""Run behavior regressions against the actual inline module UI JavaScript."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_async_module_ui_behaviors() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is needed only for the deterministic UI development harness.")
    result = subprocess.run(
        [
            node,
            str(ROOT / "scripts/check_module_ui.mjs"),
            str(ROOT / "src/ds60sqlpy/assets/learning_modules.html"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(result.stdout.splitlines()[-1])
    assert receipt == {"checks": 36, "passed": True, "final": True}
