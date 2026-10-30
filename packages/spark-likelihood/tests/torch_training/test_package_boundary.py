"""One-wheel namespace and import boundary checks for the candidate source."""

from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

from ds60_torch_training.launch import run_training


def test_public_launcher_has_no_fault_hook():
    assert "test_gate_token" not in inspect.signature(run_training).parameters


def test_training_namespace_import_stays_lazy():
    source = Path(__file__).resolve().parents[2] / "src"
    code = (
        "import json, sys; "
        f"sys.path.insert(0, {str(source)!r}); "
        "import ds60_torch_training; "
        "print(json.dumps({'torch': 'torch' in sys.modules, "
        "'pyspark': 'pyspark' in sys.modules}))"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert json.loads(result.stdout) == {"torch": False, "pyspark": False}
