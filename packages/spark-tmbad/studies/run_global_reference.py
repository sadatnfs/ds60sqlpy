"""Run the exact low-rank Gaussian sufficient-statistic reference on tiny original data."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

from global_gaussian import combine, dense_oracle, evaluate, summarize
from study_support import canonical, normal


def fixture() -> list[dict]:
    rows = []
    for i in range(16):
        x = -1 + 2 * i / 15
        z = [math.sin(math.pi * x), math.cos(math.pi * x)]
        rows.append(
            {
                "row_id": i,
                "x": [1.0, x],
                "z": z,
                "y": 0.3
                + 0.8 * x
                + 0.7 * z[0]
                - 0.4 * z[1]
                + 0.5 * normal(1901, "global_reference", i),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Keep earlier evidence; choose a new output path")
    rows = fixture()
    base = [[1.0, 0.25], [0.25, 1.4]]
    theta = [0.2, 0.7, math.log(0.6), math.log(0.9)]
    full = summarize(0, rows, 2, 2)
    parts = [
        summarize(i, values, 2, 2) for i, values in enumerate([rows[:3], [], rows[3:9], rows[9:]])
    ]
    merged = combine(
        parts, expected_partitions=4, expected_rows=len(rows), expected_ledger=full["ledger"]
    )
    observed = evaluate(merged, theta, base)
    reference = dense_oracle(rows, theta, base)
    if not math.isclose(observed["value"], reference, rel_tol=1e-11, abs_tol=1e-11):
        raise AssertionError("Bounded-statistic value disagrees with the independent dense oracle")
    errors = []
    for step in (1e-4, 1e-5):
        for j in range(len(theta)):
            plus, minus = theta.copy(), theta.copy()
            plus[j] += step
            minus[j] -= step
            numerical = (dense_oracle(rows, plus, base) - dense_oracle(rows, minus, base)) / (
                2 * step
            )
            errors.append(abs(numerical - observed["gradient"][j]))
    if max(errors) > 2e-6:
        raise AssertionError("Analytic score disagrees with independent dense differences")
    incorrect = sum(
        evaluate(summarize(i, part, 2, 2), theta, base)["value"]
        for i, part in enumerate([rows[:8], rows[8:]])
    )
    if abs(incorrect - observed["value"]) < 0.01:
        raise AssertionError("The changed latent independence model was not distinguished")
    report = {
        "schema_version": 1,
        "kind": "global-gaussian-sufficient-statistic-reference",
        "status": "passed",
        "execution": (
            "standard-library mathematical reference only; "
            "partitions are explicit fixture slices, not actual Spark tasks"
        ),
        "fixture_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "rows": len(rows),
        "partitions": [3, 0, 6, 7],
        "fixed_parameters": theta,
        "parameter_purpose": "fixed_parameter_reference",
        "base_latent_covariance": base,
        "result": observed,
        "dense_reference_value": reference,
        "maximum_score_error": max(errors),
        "incorrect_independent_partition_marginal_value": incorrect,
        "gram_scalars": 25,
        "count_scalars": 1,
        "source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("run_global_reference.py", "global_gaussian.py", "study_support.py")
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(canonical(report) + b"\n")
    print(
        canonical(
            {
                "status": "passed",
                "execution": report["execution"],
                "value_error": abs(reference - observed["value"]),
                "maximum_score_error": max(errors),
                "path": str(args.output),
            }
        ).decode()
    )


if __name__ == "__main__":
    main()
