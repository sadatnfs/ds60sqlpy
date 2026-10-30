"""Serial reproducible reference studies with retained failures and Monte Carlo error."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path

from client import run_case


def aggregate(records, requested, *, fixed_dataset=False):
    passed = [record for record in records if record.get("status") == "passed"]
    errors = [
        record["result"]["metrics"]["primary_estimate"] - record["result"]["metrics"]["truth"]
        for record in passed
    ]
    if any(not math.isfinite(value) for value in errors):
        raise ValueError("Nonfinite returned estimate cannot be admitted")
    result = {
        "requested_replications": requested,
        "attempted_replications": len(records),
        "successful_replications": len(passed),
        "failed_replications": len(records) - len(passed),
        "completion": "complete" if len(records) == requested else "incomplete",
        "interpretation": "bias/MSE conditional on successful fits; failures are retained",
    }
    fixture_hashes = [record.get("result", {}).get("fixture_sha256") for record in passed]
    known_hashes = [value for value in fixture_hashes if value is not None]
    repeated_fixture = len(known_hashes) != len(set(known_hashes))
    dataset_mcse = not fixed_dataset and not repeated_fixture
    result.update(
        simulation_unit="posterior-draw checks on fixed data" if fixed_dataset else "dataset",
        distinct_observed_dataset_hashes=len(set(known_hashes)),
        repeated_observed_dataset=bool(repeated_fixture),
        dataset_monte_carlo_uncertainty=dataset_mcse,
    )
    if not dataset_mcse:
        result["interpretation"] = (
            "Descriptive bias/MSE across repeated fixed data; no independent-dataset MCSE. "
            "Posterior-draw Monte Carlo errors, when available, remain in each case result."
        )
    if errors:
        squares = [value * value for value in errors]
        result.update(
            bias=statistics.mean(errors),
            mse=statistics.mean(squares),
            bias_mcse=statistics.stdev(errors) / math.sqrt(len(errors))
            if len(errors) > 1 and dataset_mcse
            else None,
            mse_mcse=statistics.stdev(squares) / math.sqrt(len(squares))
            if len(squares) > 1 and dataset_mcse
            else None,
        )
    predictive_errors = [record["result"]["metrics"].get("mse") for record in passed]
    if predictive_errors and all(value is not None for value in predictive_errors):
        if any(not math.isfinite(value) or value < 0 for value in predictive_errors):
            raise ValueError("Invalid held-out predictive MSE")
        result["prediction_mse_conditional_on_success"] = statistics.mean(predictive_errors)
        result["prediction_mse_mcse_across_datasets"] = (
            statistics.stdev(predictive_errors) / math.sqrt(len(predictive_errors))
            if len(predictive_errors) > 1 and dataset_mcse
            else None
        )
    coverage = [record["result"]["metrics"].get("pointwise_coverage") for record in passed]
    if coverage and all(value is not None for value in coverage):
        result["conditional_pointwise_coverage"] = statistics.mean(coverage)
        result["procedural_pointwise_coverage"] = sum(coverage) / len(records)
        result["coverage_mcse_across_independent_datasets"] = (
            statistics.stdev(coverage) / math.sqrt(len(coverage))
            if len(coverage) > 1 and dataset_mcse
            else None
        )
    if records:
        failures = len(records) - len(passed)
        # Wilson interval also remains informative for zero observed failures.
        n, z = len(records), 1.959963984540054
        observed = failures / n
        center = (observed + z * z / (2 * n)) / (1 + z * z / n)
        radius = (
            z * math.sqrt(observed * (1 - observed) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        )
        result["failure_rate"] = observed
        result["failure_rate_wilson95"] = (
            [center - radius, center + radius] if dataset_mcse else None
        )
    result["coverage_claim"] = (
        "A few smoke repetitions are execution evidence, not a calibration guarantee"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--option", action="append", default=[])
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--replications", type=int, default=3)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time-budget", type=int, default=600)
    args = parser.parse_args()
    if not 1 <= args.replications <= 5000 or not 30 <= args.time_budget <= 86400:
        raise ValueError("Declare1..5000replications and a bounded30..86400second budget")
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("Choose a fresh simulation directory")
    args.output.mkdir(parents=True)
    options = {}
    for item in args.option:
        name, separator, value = item.partition("=")
        if not separator or name in options:
            raise ValueError("Options must be unique NAME=VALUE pairs")
        options[name] = value
    records = []
    started = time.monotonic()
    for replicate in range(args.replications):
        remaining = args.time_budget - (time.monotonic() - started)
        if remaining < 10:
            break
        seed = args.seed + replicate * 7919
        try:
            result = run_case(
                args.case,
                seed=seed,
                options=options,
                prepared=args.prepared,
                output=args.output / f"replicate-{replicate:05d}",
                timeout=max(10, min(300, int(remaining))),
            )
        except Exception as error:
            result = {
                "status": "failed",
                "error": {"type": type(error).__name__, "message": str(error)[:1000]},
            }
        records.append({**result, "replicate": replicate, "seed": seed})
        (args.output / "ledger.json").write_text(
            json.dumps(records, indent=2, allow_nan=False) + "\n"
        )
    # This registered case changes posterior draws across seeds but deliberately
    # keeps the regression data fixed for its exact soft-threshold oracle.
    summary = aggregate(
        records, args.replications, fixed_dataset=args.case == "regularization_posterior"
    )
    summary["elapsed_seconds"] = time.monotonic() - started
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
