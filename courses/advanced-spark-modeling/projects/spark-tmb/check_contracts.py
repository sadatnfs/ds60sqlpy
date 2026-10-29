"""Actual R integer rejection and legacy artifact-tampering refusal."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from spark_tmb.fixed_bridge import ObjectiveError, PreparedTMB, evaluate_r, request_for
from spark_tmb.processes import cleanup_process_group
from spark_tmb.registry import ModelContractError, payload_for

ROOT = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models"))


def run_checks():
    evidence = []
    try:
        payload_for(ROOT, "normal_mean", {"y": [1, 2**53 + 1]}, [0, 0])
    except ModelContractError as error:
        assert "not exactly representable" in str(error)
    else:
        raise AssertionError("Inexact integer measurement was silently rounded")
    evidence.append({"check": "real-vector-integer-precision", "rejected_before_R_execution": True})
    with tempfile.TemporaryDirectory(prefix="tmb-contract-check-") as directory:
        temporary = Path(directory)
        for label, invalid in [
            ("integer-upper", 2147483648),
            ("integer-na-sentinel", -2147483648),
            ("integer-beyond-float-exactness", 9007199254740993),
            ("fractional", 0.5),
            ("boolean", True),
        ]:
            request = {
                "schema_version": 1,
                "action": "evaluate",
                "model_id": "random_intercept",
                "data": {"y": [1, 2], "group": [0, invalid]},
                "parameters": {},
                "theta": [0, 0, 0],
                "random": "u",
            }
            path = temporary / (label + ".json")
            path.write_text(json.dumps(request, allow_nan=False))
            process = subprocess.Popen(
                [
                    "Rscript",
                    "--vanilla",
                    str(ROOT / "R/evaluate_registered.R"),
                    str(ROOT),
                    str(BUILD),
                    str(path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=10)
            finally:
                cleanup_process_group(process)
            expected = b"booleans" if label == "boolean" else b"signed32"
            if process.returncode == 0 or expected not in stderr:
                raise AssertionError((label, process.returncode, stdout, stderr))
            evidence.append({"check": label, "rejected_by_actual_R": True})
        copied = temporary / "changed-source"
        shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
        source = copied / "models/normal_mean.cpp"
        text = source.read_text()
        if "return nll;" not in text:
            raise AssertionError("Normal model fixture no longer matches this tamper test")
        source.write_text(text.replace("return nll;", "return nll + Type(123);"))
        request = request_for(
            "normal_mean",
            [
                {"row_id": "a", "group_id": "g", "y": 1},
                {"row_id": "b", "group_id": "g", "y": 2},
            ],
            [0, 0],
        )
        try:
            evaluate_r(request, PreparedTMB(str(copied), str(BUILD)))
        except ObjectiveError as exc:
            if "source changed" not in str(exc):
                raise
        else:
            raise AssertionError("Changed source was accepted against an old compiled artifact")
        evidence.append(
            {"check": "fixed-bridge-source-tamper", "rejected_before_R_execution": True}
        )
    return evidence


if __name__ == "__main__":
    print(json.dumps({"case": "runtime-contracts", "checks": run_checks()}))
