"""Versioned one-request JSON CLI over the same prepared-model contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .registry import ModelContractError
from .runtime import (
    PROJECT_ROOT,
    describe_prepared,
    evaluate_prepared,
    fit_prepared,
    predict_prepared,
)

MAX_BYTES = 1_000_000


def _object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ModelContractError("Duplicate JSON key")
        result[name] = value
    return result


def _constant(value):
    raise ModelContractError("JSON numbers must be finite")


def handle(request, *, root=None, build_dir=None):
    import os

    root = PROJECT_ROOT if root is None else Path(root)
    build_dir = build_dir or os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models")
    if not isinstance(request, dict) or type(request.get("schema_version")) is not int:
        raise ModelContractError("Use integer schema_version=1")
    if request["schema_version"] != 1 or not isinstance(request.get("model_id"), str):
        raise ModelContractError("Unknown schema or invalid model identifier")
    operation = request.get("operation")
    if not isinstance(operation, str):
        raise ModelContractError("Operation must be a string")
    required = {"schema_version", "operation", "model_id"}
    if operation in {"evaluate", "fit"}:
        required |= {"data", "parameters"}
    elif operation == "predict":
        required |= {"data", "parameters", "n_rows", "target"}
    elif operation != "describe":
        raise ModelContractError("Operation must be describe, evaluate, fit or predict")
    if set(request) != required:
        raise ModelContractError("Request keys differ from the fixed versioned contract")
    model = request["model_id"]
    if operation == "describe":
        result = describe_prepared(model, root=root, build_dir=build_dir)
    elif operation == "predict":
        result = predict_prepared(
            model,
            request["data"],
            request["parameters"],
            n_rows=request["n_rows"],
            target=request["target"],
            root=root,
            build_dir=build_dir,
        )
    else:
        function = evaluate_prepared if operation == "evaluate" else fit_prepared
        result = function(
            model, request["data"], request["parameters"], root=root, build_dir=build_dir
        )
    return {"schema_version": 1, "operation": operation, "model_id": model, "result": result}


def main():
    try:
        payload = sys.stdin.buffer.read(MAX_BYTES + 1)
        if not payload or len(payload) > MAX_BYTES:
            raise ModelContractError("Request must be 1..1000000 UTF-8 bytes")
        request = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_object, parse_constant=_constant
        )
        result = handle(request)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError, subprocess.TimeoutExpired) as exc:
        diagnostic = {
            "schema_version": 1,
            "error": {"type": type(exc).__name__, "message": str(exc)[:2048]},
        }
        print(json.dumps(diagnostic, allow_nan=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
