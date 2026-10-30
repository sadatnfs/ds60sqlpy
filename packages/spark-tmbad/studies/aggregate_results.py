"""Aggregate completed Monte Carlo shards with explicit failed-fit accounting."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from study_support import aggregate, bounded_json, canonical, digest, scalar_summary, wilson


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple, list[dict[str, Any]]] = {}
    truths = {}
    configurations = {}
    seen = set()
    for report in reports:
        if (
            report.get("kind") != "original-spark-modeling-study"
            or report.get("status") != "completed"
        ):
            raise ValueError(
                "Interrupted, planned or unrelated results are not completed replications"
            )
        identity = (report["backend"], report["study"], report["seed"], report["replicate"])
        if identity in seen:
            raise ValueError("Duplicate Monte Carlo replication")
        seen.add(identity)
        environment = digest(
            {
                "package": report["package_identity"],
                "artifact": report.get("artifact_identity"),
                "runtime": report["runtime_versions"],
                "spark": report["spark_version"],
                "source": report["study_source_sha256"],
                "generator": report["generator_sha256"],
            }
        )
        for row in report["records"]:
            key = (report["backend"], report["study"], row["scenario"], row["method"])
            configuration = {
                "environment": environment,
                "truth": row["truth"],
                "initial": row["canonical_initial"],
                "l2_strength": row["l2_strength"],
                "training_rows": row["training_rows"],
                "future_rows": row["future_rows"],
                "optimizer": report["optimizer_settings"],
            }
            if key in configurations and configurations[key] != configuration:
                raise ValueError(
                    "Do not pool changed targets, source/runtime artifacts or settings"
                )
            configurations[key] = configuration
            truths[key] = row["truth"]
            groups.setdefault(key, []).append(row)
    output = []
    for key, records in sorted(groups.items()):
        result = {
            "backend": key[0],
            "study": key[1],
            "scenario": key[2],
            "method": key[3],
            "configuration": configurations[key],
            "parameters": aggregate(records, truths[key]),
        }
        passed = [row for row in records if row["status"] == "passed"]
        if passed:
            cohorts = set(passed[0]["future_metrics"])
            if any(set(row["future_metrics"]) != cohorts for row in passed):
                raise ValueError("Forecast cohort coverage changed across replications")
            metrics = {}
            for cohort in sorted(cohorts):
                metrics[cohort] = {}
                for metric in (
                    "mse",
                    "mean_marginal_nll",
                    "pointwise_coverage",
                    "unadjusted_pointwise_bands_joint_coverage",
                ):
                    values = [row["future_metrics"][cohort][metric] for row in passed]
                    metrics[cohort][metric] = {"conditional_on_success": scalar_summary(values)}
                    if "coverage" in metric:
                        # First average within each independent simulated dataset;
                        # failed fits contribute zero to procedural coverage.
                        procedural = [
                            row["future_metrics"][cohort][metric]
                            if row["status"] == "passed"
                            else 0.0
                            for row in records
                        ]
                        metrics[cohort][metric]["procedural_over_all_attempts"] = scalar_summary(
                            procedural
                        )
            result["future_metrics"] = metrics
        result["failure_rate"] = wilson(
            sum(row["status"] == "failed" for row in records), len(records)
        )
        output.append(result)
    if not output:
        raise ValueError("No completed study results to aggregate")
    return {
        "schema_version": 1,
        "kind": "modeling-monte-carlo-summary",
        "status": "completed",
        "groups": output,
        "scope": "MCSE across independent generated datasets; conditional estimates and procedural coverage are separate; small replication counts are not calibration evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", nargs="+", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Keep previous results; select a new output path")
    if len(args.reports) > 10000:
        raise ValueError("Aggregate at most10000 study shards at once")
    result = summarize([bounded_json(path) for path in args.reports])
    body = canonical(result) + b"\n"
    if len(body) > 4 * 1024 * 1024:
        raise ValueError("Summary exceeds4MiB; aggregate separate scenarios")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        f.write(body)
    print(
        canonical(
            {"status": "completed", "groups": len(result["groups"]), "path": str(args.output)}
        ).decode()
    )


if __name__ == "__main__":
    main()
