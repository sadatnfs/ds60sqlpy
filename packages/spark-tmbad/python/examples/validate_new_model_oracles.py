# SPDX-License-Identifier: MIT
"""Independent, serial framed-process comparison of retained high precision cases.

No Spark, Python facade, optimizer, cloud, posterior sampler or deployment is
qualified by this runner. Each native evaluation uses a fresh process. Thresholds
are fixed before execution; historical references and receipts are never edited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import struct
import subprocess
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

LIMIT = 4 * 1024 * 1024
PROFILES = {
    "ordinary": {
        "value": [3e-8, 3e-7],
        "gradient": [3e-8, 3e-7],
        "hessian": [2e-5, 2e-5],
        "moments": [3e-8, 3e-7],
    },
    "tiny_positive": {
        "value": [3e-8, 1e-24],
        "gradient": [3e-8, 1e-24],
        "hessian": [2e-5, 1e-22],
        "moments": [3e-8, 1e-24],
    },
    "gamma_endpoint": {
        "value": [3e-8, 1e-12],
        "gradient": [3e-8, 1e-12],
        "hessian": [2e-5, 1e-12],
        "moments": [3e-8, 1e-12],
    },
    "series": {
        "value": [3e-8, 1e-24],
        "gradient": [3e-8, 1e-24],
        "hessian": [2e-5, 1e-22],
        "moments": [3e-8, 1e-24],
    },
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("Nonfinite JSON token: " + value)


def loads(value):
    return json.loads(value, object_pairs_hook=unique, parse_constant=invalid_constant)


def payload(value):
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()


def compare(actual, expected, tolerances, label="value"):
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(f"{label}: shape differs")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            compare(left, right, tolerances, f"{label}[{index}]")
        return
    reference = float(expected)
    if (
        isinstance(actual, bool)
        or not isinstance(actual, (int, float))
        or not math.isfinite(actual)
        or not math.isfinite(reference)
        or not math.isclose(actual, reference, rel_tol=tolerances[0], abs_tol=tolerances[1])
    ):
        raise AssertionError(
            f"{label}: native={actual!r}, reference={expected!r}, limits={tolerances}"
        )


def response_frame(raw):
    if not 4 < len(raw) <= LIMIT + 4:
        raise AssertionError("Native response outside frame bound")
    if struct.unpack(">I", raw[:4])[0] != len(raw) - 4:
        raise AssertionError("Incomplete response or extra native output")
    return loads(raw[4:])


class Native:
    def __init__(self, manifest_path, output, budget_seconds=240):
        self.manifest = loads(Path(manifest_path).read_bytes())
        self.output = Path(output)
        self.started = time.monotonic()
        self.budget_seconds = budget_seconds
        self.calls = 0
        self.models = {item["id"]: item for item in self.manifest["models"]}
        architecture = {"aarch64": "arm64", "x86_64": "amd64"}.get(
            platform.machine(), platform.machine()
        )
        if (
            platform.system() != "Linux"
            or self.manifest["platform"] != {"os": "linux", "arch": architecture}
            or self.manifest["package_version"] != "0.2.0"
            or len(self.models) != 23
        ):
            raise ValueError(
                "Qualification requires coherent native Linux 0.2.0 artifact with 23 models"
            )
        self.binary = Path(self.manifest["binary"]["path"])
        if digest(self.binary) != self.manifest["binary"]["sha256"]:
            raise ValueError("Binary differs from manifest")
        described = subprocess.run(
            [str(self.binary), "--describe"],
            capture_output=True,
            timeout=30,
            check=True,
        )
        description = loads(described.stdout)
        for key in ("build_id", "engine", "models"):
            if description[key] != self.manifest[key]:
                raise ValueError("Live native description differs: " + key)
        (self.output / "native-description.json").write_text(
            json.dumps(description, indent=2) + "\n"
        )

    def call(self, model, operation, theta, rows, expected_error=None, **extra):
        remaining = self.budget_seconds - (time.monotonic() - self.started)
        if remaining <= 1:
            raise TimeoutError("Total native qualification budget exhausted")
        self.calls += 1
        descriptor = self.models[model]
        request = {
            "protocol": 1,
            "request_id": f"new-model-oracle-{self.calls}",
            "op": operation,
            "model_id": model,
            "model_digest": descriptor["digest"],
            "theta": theta,
            "rows": rows,
            **extra,
        }
        encoded = payload(request)
        process = subprocess.run(
            [str(self.binary), "--stdio"],
            input=struct.pack(">I", len(encoded)) + encoded,
            capture_output=True,
            timeout=min(30, remaining),
            check=False,
        )
        entry = {
            "request": request,
            "request_sha256": hashlib.sha256(encoded).hexdigest(),
            "exit_code": process.returncode,
            "stderr": process.stderr[:8192].decode(errors="replace"),
            "stdout_sha256": hashlib.sha256(process.stdout).hexdigest(),
        }
        try:
            response = response_frame(process.stdout)
            entry["response"] = response
        finally:
            with (self.output / "requests.jsonl").open("a") as stream:
                stream.write(json.dumps(entry, allow_nan=False, sort_keys=True) + "\n")
        expected = {
            "protocol": 1,
            "request_id": request["request_id"],
            "request_sha256": entry["request_sha256"],
            "model_id": model,
            "model_digest": descriptor["digest"],
            "build_id": self.manifest["build_id"],
            "status": "error" if expected_error else "ok",
        }
        if any(response.get(key) != value for key, value in expected.items()):
            raise AssertionError("Native identity/status mismatch")
        if process.returncode != (2 if expected_error else 0):
            raise AssertionError("Native process did not finish with required exit status")
        if expected_error and response.get("error", {}).get("code") != expected_error:
            raise AssertionError("Unexpected native refusal code")
        return response


def moments(reference):
    return [
        [
            float(item["mean"]),
            float(item["variance"]),
            math.sqrt(float(item["variance"])),
        ]
        for item in reference
    ]


def row_check(native, case):
    family, name = case["family"], case["case"]
    profile_name = case.get("profile", "ordinary")
    if family == "beta_binomial" and name.startswith("extreme_probability"):
        profile_name = "gamma_endpoint"
    elif family == "zero_truncated_poisson" and name == "near_zero_singleton":
        profile_name = "tiny_positive"
    profile = PROFILES[profile_name]
    result = native.call(
        family,
        "evaluate",
        case["parameters"],
        case["rows"],
        kind="rows",
        weights=case["weights"],
        hessian=True,
    )
    compare(result["loss"], case["value"], profile["value"], "loss")
    compare(result["gradient"], case["gradient"], profile["gradient"], "gradient")
    compare(
        result["hessian"],
        [value for row in case["hessian"] for value in row],
        profile["hessian"],
        "hessian",
    )
    if family == "student_t_regression" and name == "finite_extreme_intercept":
        compare(
            result["gradient"][:2],
            case["gradient"][:2],
            [3e-8, 0],
            "representable extreme gradient",
        )
    if result["row_count"] != len(case["rows"]) or result["unit_count"] != 0:
        raise AssertionError("Row count ledger differs")
    compare(result["weight_sum"], sum(case["weights"]), [0, 0], "weight ledger")
    for operation in ("predict", "forecast"):
        prediction = native.call(
            family,
            operation,
            case["parameters"],
            case["future"],
            target="response",
            history=[],
        )
        if prediction["columns"] != ["mean", "variance", "sd"]:
            raise AssertionError("Unexpected response-moment columns")
        compare(
            prediction["values"],
            moments(case["prediction_and_forecast_moments"]),
            profile["moments"],
            operation,
        )
    return {"family": family, "case": name, "profile": profile_name, "status": "passed"}


def gaussian_check(native, case):
    model = "gaussian_correlated_random_slope"
    result = native.call(
        model,
        "evaluate",
        case["parameters"],
        case["history"],
        kind="unit",
        unit_weight=1.0,
        hessian=True,
    )
    for field, reference in (
        ("loss", "value"),
        ("gradient", "gradient"),
        ("hessian", "hessian"),
    ):
        expected = (
            [value for row in case[reference] for value in row]
            if field == "hessian"
            else case[reference]
        )
        compare(result[field], expected, PROFILES["ordinary"][reference], field)
    if (
        result["unit_count"] != 1
        or result["row_count"] != len(case["history"])
        or result["weight_sum"] != 1
    ):
        raise AssertionError("Complete-unit ledger differs")
    for target in ("existing_group", "new_group"):
        reference = case[target]
        expected = moments(
            [
                {"mean": mean, "variance": reference["covariance"][i][i]}
                for i, mean in enumerate(reference["mean"])
            ]
        )
        for operation in ("predict", "forecast"):
            prediction = native.call(
                model,
                operation,
                case["parameters"],
                [[x] for x in case["future"]],
                target=target,
                history=case["history"] if target == "existing_group" else [],
            )
            if prediction["columns"] != ["mean", "variance", "sd"]:
                raise AssertionError("Unexpected Gaussian columns")
            compare(
                prediction["values"],
                expected,
                PROFILES["ordinary"]["moments"],
                target + ":" + operation,
            )
    return {
        "family": model,
        "case": case["case"],
        "profile": "ordinary",
        "status": "passed",
    }


def refusals(native):
    cases = [
        ("binomial_logistic", [0, 0], [[0, 3, 4]]),
        ("binomial_logistic", [0, 0], [[0, 0, 1]]),
        ("beta_binomial", [0, 0, 0], [[0, 2.5, 1]]),
        ("beta_regression", [0, 0, 0], [[0, 0]]),
        ("beta_regression", [0, 0, 0], [[0, 1]]),
        ("lognormal_regression", [0, 0, 0], [[0, 0]]),
        ("student_t_regression", [0, 0, 0, 0], [[0, 1e13]]),
        ("zero_truncated_poisson", [0, 0], [[0, 1, 0]]),
        ("zero_inflated_poisson", [0, 0, 0, 0], [[0, 0, 1, -1]]),
        ("hurdle_poisson", [0, 0, 0, 0], [[0, 0, 1e-7, 1]]),
    ]
    for model, theta, rows in cases:
        native.call(
            model,
            "evaluate",
            theta,
            rows,
            kind="rows",
            weights=[1],
            hessian=True,
            expected_error="DOMAIN_ERROR",
        )
    return len(cases)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--gaussian", type=Path, required=True)
    parser.add_argument("--supplement", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "running",
        "scope": "Actual native framed-process F/G/H, response-free moments and domain refusals only; no Spark or optimization",
        "started_utc": datetime.now(UTC).isoformat(),
        "thresholds": PROFILES,
        "threshold_policy": "Ordinary/tiny thresholds preserved from existing row oracle. New gamma endpoint absolute thresholds fixed before first execution to expose the retained 1.26e-9 cancellation regression.",
        "inputs_sha256": {
            key: digest(getattr(args, key))
            for key in ("manifest", "rows", "gaussian", "supplement")
        },
        "runner_sha256": digest(__file__),
        "cases": [],
        "failures": [],
    }
    native = None
    try:
        native = Native(args.manifest, args.output)
        report.update(
            {
                "build_id": native.manifest["build_id"],
                "binary_sha256": native.manifest["binary"]["sha256"],
                "engine": native.manifest["engine"],
                "model_digests": {key: val["digest"] for key, val in native.models.items()},
            }
        )
        extra = loads(args.supplement.read_bytes())
        rows = loads(args.rows.read_bytes())["results"] + extra["rows"]
        gaussian = loads(args.gaussian.read_bytes())["results"] + extra["gaussian"]
        for function, cases in ((row_check, rows), (gaussian_check, gaussian)):
            for case in cases:
                try:
                    report["cases"].append(function(native, case))
                except Exception as error:  # noqa: BLE001 - retain every failure and exit nonzero.
                    report["failures"].append(
                        {
                            "family": case.get("family", "gaussian_correlated_random_slope"),
                            "case": case["case"],
                            "error": repr(error),
                        }
                    )
                    print("FAILED " + case["case"] + ": " + str(error), flush=True)
        try:
            report["domain_refusal_cases"] = refusals(native)
        except Exception as error:  # noqa: BLE001 - retain every failure and exit nonzero.
            report["failures"].append({"case": "domain_refusals", "error": repr(error)})
        report["case_counts"] = dict(Counter(item["family"] for item in report["cases"]))
        report["status"] = "failed" if report["failures"] else "passed"
    except Exception as error:  # noqa: BLE001 - retain every failure and exit nonzero.
        report["status"] = "failed"
        report["failures"].append({"case": "initialization_or_budget", "error": repr(error)})
    finally:
        report["native_process_requests"] = native.calls if native else 0
        report["finished_utc"] = datetime.now(UTC).isoformat()
        (args.output / "QUALIFICATION.json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n"
        )
    print(
        json.dumps(
            {key: report[key] for key in ("status", "native_process_requests", "failures")},
            indent=2,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
