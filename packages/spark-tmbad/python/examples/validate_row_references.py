"""Run actual native row-model requests against separately generated references."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from validate_native_oracles import NativeHarness


def compare(actual, expected, tolerance, absolute):
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError("Native output shape differs from reference")
        for left, right in zip(actual, expected):
            compare(left, right, tolerance, absolute)
    elif not math.isfinite(actual) or not math.isclose(
        actual, expected, rel_tol=tolerance, abs_tol=absolute
    ):
        raise AssertionError(
            f"Native value {actual!r} differs from independent reference {expected!r}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--references", required=True, type=Path)
    args = parser.parse_args()
    references = json.loads(args.references.read_text())
    native = NativeHarness(args.manifest)
    counts = {}
    for case in references["cases"]:
        model_id, theta, rows = case["model_id"], case["theta"], case["rows"]
        try:
            result = native.call(
                model_id,
                "evaluate",
                theta,
                rows,
                kind="rows",
                weights=[1.0] * len(rows),
                hessian=True,
            )
            absolute = 1e-24 if case["tiny_positive_loss"] else 3e-7
            compare(result["loss"], case["expected"]["loss"], 3e-8, absolute)
            compare(result["gradient"], case["expected"]["gradient"], 3e-8, absolute)
            for expected in case["expected"]["hessians"]:
                compare(
                    result["hessian"], expected, 2e-5, 1e-22 if case["tiny_positive_loss"] else 2e-5
                )
            for operation in ("predict", "forecast"):
                output = native.call(
                    model_id, operation, theta, case["future"], target="response", history=[]
                )
                compare(
                    output["values"],
                    case["future_expected"],
                    3e-8,
                    1e-24 if case["tiny_positive_loss"] else 3e-7,
                )
            counts[model_id] = counts.get(model_id, 0) + 1
        except Exception as error:
            raise AssertionError(
                f"Row-model reference case failed: {model_id}, theta={theta}, rows={rows}"
            ) from error
    report = {
        "status": "passed",
        "scope": "actual native row-model F/G/H and target checks; no Spark",
        "build_id": native.manifest["build_id"],
        "binary_sha256": native.manifest["binary"]["sha256"],
        "reference_sha256": hashlib.sha256(args.references.read_bytes()).hexdigest(),
        "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scipy_reference_version": references["scipy_version"],
        "parameter_data_cases": counts,
        "native_process_calls": native.calls,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
