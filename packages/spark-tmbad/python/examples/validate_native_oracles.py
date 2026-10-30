"""Direct native protocol checks against independent analytic references.

This is native-only evidence. It does not start Spark or qualify the JVM bridge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import struct
import subprocess
from pathlib import Path

from ds60_spark_tmbad import PreparedRuntime
from ds60_spark_tmbad._json import MAX_JSON_BYTES, dumps, loads
from numerical_oracles import (
    ar1_forecast,
    finite_difference_hessian,
    gaussian_ar1_random_intercept,
    gaussian_ar1_random_intercept_prediction,
    gaussian_random_intercept,
    gaussian_random_intercept_prediction,
    poisson_random_intercept,
    poisson_random_intercept_prediction,
    poisson_random_slope,
    poisson_random_slope_prediction,
)


def close(actual, expected, tolerance=2e-7):
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(f"Shape mismatch: {actual!r}; expected {expected!r}")
        for observed, reference in zip(actual, expected, strict=True):
            close(observed, reference, tolerance)
    elif (
        isinstance(actual, bool)
        or not math.isfinite(actual)
        or not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)
    ):
        raise AssertionError(f"Numerical mismatch: {actual!r}; expected {expected!r}")


class NativeHarness:
    def __init__(self, manifest_path):
        self.runtime = PreparedRuntime.from_manifest(manifest_path, verify_files=False)
        self.manifest = self.runtime.manifest
        architecture = {"aarch64": "arm64", "x86_64": "amd64"}.get(
            platform.machine(), platform.machine()
        )
        if platform.system() != "Linux" or architecture != self.manifest["platform"]["arch"]:
            raise RuntimeError("Run native checks on the manifest's native Linux architecture")
        self.binary = Path(self.manifest["binary"]["path"])
        digest = hashlib.sha256()
        with self.binary.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != self.manifest["binary"]["sha256"]:
            raise RuntimeError("Native binary hash differs from the prepared manifest")
        self.calls = 0

    def call(self, model_id, operation, theta, rows, **extra):
        self.calls += 1
        descriptor = self.runtime.descriptor(model_id)
        request = {
            "protocol": 1,
            "request_id": f"independent-oracle-{self.calls}",
            "op": operation,
            "model_id": model_id,
            "model_digest": descriptor["digest"],
            "theta": theta,
            "rows": rows,
            **extra,
        }
        payload = dumps(request).encode("utf-8")
        process = subprocess.run(
            [str(self.binary), "--stdio"],
            input=struct.pack(">I", len(payload)) + payload,
            capture_output=True,
            timeout=45,
            check=False,
        )
        # A valid-looking response remains provisional until the worker exits 0.
        if process.returncode != 0:
            raise RuntimeError(
                f"Native process exited {process.returncode}: "
                + process.stderr[:8192].decode("utf-8", errors="replace")
            )
        if len(process.stdout) < 4 or len(process.stdout) > MAX_JSON_BYTES + 4:
            raise AssertionError("Native response length is outside the frame bound")
        length = struct.unpack(">I", process.stdout[:4])[0]
        if length != len(process.stdout) - 4:
            raise AssertionError("Native response is incomplete or contains extra frames/bytes")
        response = loads(process.stdout[4:])
        expected = {
            "protocol": 1,
            "request_id": request["request_id"],
            "request_sha256": hashlib.sha256(payload).hexdigest(),
            "model_id": model_id,
            "model_digest": descriptor["digest"],
            "build_id": self.manifest["build_id"],
            "status": "ok",
        }
        if any(response.get(key) != value for key, value in expected.items()):
            raise AssertionError(f"Native response identity/status mismatch: {response}")
        return response


def gaussian_checks(native):
    count = 0
    for observations in ([1.2, -0.4, 2.8], [-3.0, -2.7, -1.5, -2.0]):
        rows = [[value] for value in observations]
        for theta in ([0.3, -0.5, 0.2], [-1.0, 0.4, -0.7]):
            reference = gaussian_random_intercept(theta, observations)
            exact = native.call(
                "gaussian_random_intercept",
                "evaluate",
                theta,
                rows,
                kind="unit",
                unit_weight=1.0,
                hessian=True,
            )
            close(exact["loss"], reference["loss"])
            close(exact["gradient"], reference["gradient"])
            for step in (2e-5, 5e-6):
                hessian = finite_difference_hessian(
                    lambda point, observations=observations: gaussian_random_intercept(
                        point, observations
                    )["gradient"],
                    theta,
                    step,
                )
                close(exact["hessian"], hessian, tolerance=5e-6)
            approximate = native.call(
                "gaussian_random_intercept_laplace",
                "evaluate",
                theta,
                rows,
                kind="unit",
                unit_weight=1.0,
            )
            close(approximate["loss"], reference["loss"])
            close(approximate["gradient"], reference["gradient"])
            weighted = native.call(
                "gaussian_random_intercept", "evaluate", theta, rows, kind="unit", unit_weight=2.5
            )
            close(weighted["loss"], 2.5 * reference["loss"])
            close(weighted["gradient"], [2.5 * item for item in reference["gradient"]])
            close(weighted["weight_sum"], 2.5)
            for operation in ("predict", "forecast"):
                for target, history in (("existing_group", rows), ("new_group", [])):
                    result = native.call(
                        "gaussian_random_intercept",
                        operation,
                        theta,
                        [[], []],
                        target=target,
                        history=history,
                    )
                    predicted = gaussian_random_intercept_prediction(
                        theta, observations if history else None
                    )
                    close(result["values"], [predicted, predicted])
                    if result["columns"] != ["mean", "variance", "sd"]:
                        raise AssertionError("Random-intercept target column order differs")
            count += 1
    return {
        "model": "gaussian_random_intercept",
        "parameter_data_cases": count,
        "checks": [
            "exact marginal F/G/H",
            "Gaussian Laplace parity",
            "whole-unit weight",
            "existing/new group predictions and forecasts",
            "parameter uncertainty excluded",
        ],
    }


def poisson_checks(native):
    count = 0
    for rows in ([[0.5, 0], [1.5, 2], [2.0, 5]], [[1.0, 0], [0.8, 0]], [[0.4, 8], [3.0, 11]]):
        for theta in ([-0.4, -0.3], [0.7, 0.2], [1.0, -1.0]):
            reference = poisson_random_intercept(theta, rows)
            result = native.call(
                "poisson_random_intercept", "evaluate", theta, rows, kind="unit", unit_weight=1.0
            )
            close(result["loss"], reference["loss"], tolerance=3e-7)
            close(result["gradient"], reference["gradient"], tolerance=3e-7)
            diagnostics = result["diagnostics"]
            close(diagnostics["mode"], [reference["mode"]], tolerance=1e-7)
            for operation in ("predict", "forecast"):
                for target, history in (("existing_group", rows), ("new_group", [])):
                    exposures = [0.75, 2.5]
                    result = native.call(
                        "poisson_random_intercept",
                        operation,
                        theta,
                        [[value] for value in exposures],
                        target=target,
                        history=history,
                    )
                    predicted = [
                        poisson_random_intercept_prediction(
                            theta, exposure, rows if history else None
                        )
                        for exposure in exposures
                    ]
                    close(result["values"], predicted, tolerance=4e-7)
            count += 1
    return {
        "model": "poisson_random_intercept",
        "parameter_data_cases": count,
        "checks": [
            "analytic scalar mode",
            "Laplace F/G with implicit curvature derivative",
            "existing-group Laplace moments",
            "new-group exact prior moments",
            "parameter uncertainty excluded",
        ],
    }


def ar1_checks(native):
    count = 0
    for theta in ([2.0, math.atanh(-0.5), math.log(0.7)], [-0.3, math.atanh(0.8), math.log(0.4)]):
        history = [[0, 1.2], [1, -0.2], [2, 0.8]]
        future = [[3], [4], [5], [6]]
        result = native.call(
            "ar1", "forecast", theta, future, target="conditional_history", history=history
        )
        close(result["values"], ar1_forecast(theta, [1, 2, 3, 4], last_observation=0.8))
        stationary = native.call(
            "ar1",
            "forecast",
            theta,
            [[10], [11], [12], [13]],
            target="stationary_new_series",
            history=[],
        )
        close(stationary["values"], ar1_forecast(theta, [1, 2, 3, 4]))
        predicted = native.call("ar1", "predict", theta, [[0.8]], target="response")
        close(predicted["values"], ar1_forecast(theta, [1], last_observation=0.8))
        count += 1
    return {
        "model": "ar1",
        "parameter_data_cases": count,
        "checks": [
            "positive/negative autocorrelation",
            "four-step innovation propagation",
            "conditional versus stationary targets",
            "one-step lag prediction",
        ],
    }


def combined_checks(native):
    count = 0
    model_id = "gaussian_ar1_random_intercept"
    for history in ([[0, 0.7], [1, -0.2], [2, 1.4], [3, 0.3]], [[4, -1.0], [5, -0.3], [6, 0.2]]):
        for theta in (
            [0.2, math.atanh(0.6), -0.4, -0.1],
            [-0.3, math.atanh(-0.4), 0.1, -0.7],
            [0.2, 0.0, -0.4, -0.1],
        ):
            reference = gaussian_ar1_random_intercept(theta, history)
            result = native.call(
                model_id, "evaluate", theta, history, kind="unit", unit_weight=1.0, hessian=True
            )
            close(result["loss"], reference["loss"])
            close(result["gradient"], reference["gradient"])
            for step in (2e-5, 5e-6):
                hessian = finite_difference_hessian(
                    lambda point, history=history: gaussian_ar1_random_intercept(point, history)[
                        "gradient"
                    ],
                    theta,
                    step,
                )
                close(result["hessian"], hessian, tolerance=8e-6)
            times = [history[-1][0] + offset for offset in (1, 2, 3)]
            for target, supplied_history in (
                ("conditional_history", history),
                ("stationary_new_series", []),
            ):
                prediction = native.call(
                    model_id,
                    "forecast",
                    theta,
                    [[time] for time in times],
                    target=target,
                    history=supplied_history,
                )
                close(
                    prediction["values"],
                    gaussian_ar1_random_intercept_prediction(
                        theta, times, supplied_history if supplied_history else None
                    ),
                )
            count += 1
    return {
        "model": model_id,
        "parameter_data_cases": count,
        "checks": [
            "independent dense-covariance marginal F/G/H",
            "positive/negative/zero AR coefficient",
            "dense Gaussian conditional forecasts",
            "stationary new-series moments",
            "parameter uncertainty excluded",
        ],
    }


def slope_checks(native):
    count = 0
    fixtures = [
        [[-1.0, 1.0, 0], [0.0, 2.0, 3], [0.7, 0.5, 2], [1.0, 1.5, 5]],
        [[-1.0, 1.0, 0], [0.3, 0.5, 0], [1.0, 2.0, 0]],
    ]
    for rows in fixtures:
        for theta in ([0.2, -0.3, -0.4, -0.7], [-0.5, 0.6, 0.1, -0.2]):
            reference = poisson_random_slope(theta, rows)
            result = native.call(
                "poisson_random_slope", "evaluate", theta, rows, kind="unit", unit_weight=1.0
            )
            close(result["loss"], reference["loss"], tolerance=5e-7)
            close(result["gradient"], reference["gradient"], tolerance=5e-7)
            close(result["diagnostics"]["mode"], reference["mode"], tolerance=2e-7)
            future = [[-0.5, 0.75], [0.8, 1.5]]
            for operation in ("predict", "forecast"):
                for target, history in (("existing_group", rows), ("new_group", [])):
                    predicted = native.call(
                        "poisson_random_slope",
                        operation,
                        theta,
                        future,
                        target=target,
                        history=history,
                    )
                    expected = [
                        poisson_random_slope_prediction(theta, x, exposure, history or None)
                        for x, exposure in future
                    ]
                    close(predicted["values"], expected, tolerance=6e-7)
            count += 1
    return {
        "model": "poisson_random_slope",
        "parameter_data_cases": count,
        "checks": [
            "analytic two-dimensional mode and total Laplace gradient",
            "full posterior covariance including off-diagonal term",
            "existing/new group predictions and future-covariate forecasts",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument(
        "--case",
        choices=["all", "core", "gaussian", "poisson", "ar1", "combined", "slope"],
        default="all",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    native = NativeHarness(args.manifest)
    checks = {
        "gaussian": gaussian_checks,
        "poisson": poisson_checks,
        "ar1": ar1_checks,
        "combined": combined_checks,
        "slope": slope_checks,
    }
    results = [
        check(native)
        for name, check in checks.items()
        if args.case in ("all", name) or (args.case == "core" and name not in ("combined", "slope"))
    ]
    report = {
        "status": "passed",
        "scope": "native-only independent numerical oracles; no Spark",
        "build_id": native.manifest["build_id"],
        "binary_sha256": native.manifest["binary"]["sha256"],
        "platform": native.manifest["platform"],
        "native_process_calls": native.calls,
        "checks": results,
        "oracle_source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("numerical_oracles.py", "validate_native_oracles.py")
        },
        "python_version": platform.python_version(),
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
