# SPDX-License-Identifier: MIT
"""Aggregate completed native0.2 shards without dropping failed fits."""

from __future__ import annotations

import argparse
from pathlib import Path

from study_support import bounded_json, canonical, digest, scalar_summary, wilson


def summarize(reports):
    groups = {}
    configurations = {}
    seen = set()
    seen_datasets = set()
    inputs = []
    for report in reports:
        if report.get("kind") != "native020-actual-study" or report.get("status") != "completed":
            raise ValueError("Only completed actual study shards may be aggregated")
        identity = (report["study"], report["seed"], report["replicate"])
        if identity in seen:
            raise ValueError("Duplicate generated dataset replication")
        seen.add(identity)
        scenarios = {record["scenario"] for record in report["planned_records"]}
        if set(report["dataset_identities"]) != scenarios:
            raise ValueError("Dataset identity coverage differs from planned scenarios")
        for scenario, dataset in report["dataset_identities"].items():
            if set(dataset) != {"training_sha256", "future_sha256"}:
                raise ValueError("Dataset identity requires both training and future bytes")
            for split, checksum in dataset.items():
                if (
                    not isinstance(checksum, str)
                    or len(checksum) != 64
                    or any(c not in "0123456789abcdef" for c in checksum)
                ):
                    raise ValueError("Invalid dataset hash")
                key = (report["study"], scenario, split, checksum)
                if key in seen_datasets:
                    raise ValueError(
                        "Repeated training or future data cannot supply independent "
                        "dataset MCSE; changing labels or posterior draws is insufficient"
                    )
                seen_datasets.add(key)
        inputs.append({"identity": list(identity), "report_sha256": digest(report)})

        def key(record):
            return (
                record[("scenario")],
                record[("method")],
                record[("reduction")],
                record[("case_sha256")],
            )

        planned = {key(r) for r in report["planned_records"]}
        actual = {key(r) for r in report["records"]}
        if (
            planned != actual
            or len(planned) != len(report["planned_records"])
            or len(actual) != len(report["records"])
        ):
            raise ValueError("Missing or duplicated planned method coverage")
        for record in report["records"]:
            if record["status"] not in {"passed", "failed"}:
                raise ValueError("Incomplete fit record")
            group = (
                report["study"],
                record["scenario"],
                record["method"],
                record["reduction"],
            )
            configuration = {
                "target": record["target_configuration"],
                "metric_schema": record["metric_schema"],
                "truth": record["truth"],
                "source": report["source_sha256"],
                "generator": report["generator_sha256"],
                "artifact": report["artifact_identity"],
                "package": report["package_identity"],
                "environment": report["environment"],
                "partitions": report["partitions"],
                "training_rows": record["training_rows"],
                "future_rows": record["future_rows"],
            }
            if group in configurations and configuration != configurations[group]:
                raise ValueError("Changed target/source/artifact/environment cannot be pooled")
            configurations[group] = configuration
            # Keep bounded analysis fields; discard individual fitted documents and traces.
            groups.setdefault(group, []).append(
                {
                    k: v
                    for k, v in record.items()
                    if k
                    in {
                        "status",
                        "parameter_errors",
                        "parameter_error_names",
                        "future_metrics",
                        "group_summary",
                    }
                }
            )
    if not groups:
        raise ValueError("No actual study records")
    output = []
    for key, records in sorted(groups.items()):
        passed = [r for r in records if r["status"] == "passed"]
        result = {
            "study": key[0],
            "scenario": key[1],
            "method": key[2],
            "reduction": key[3],
            "configuration": configurations[key],
            "attempted_replications": len(records),
            "successful_replications": len(passed),
            "replication_failure_fraction": wilson(len(records) - len(passed), len(records)),
        }
        if any("group_summary" in record for record in records):
            if not all("group_summary" in record for record in records):
                raise ValueError("Mixed individual and grouped fit accounting")
            attempted = sum(record["group_summary"]["groups"] for record in records)
            successful = sum(record["group_summary"]["successful_groups"] for record in records)
            result["group_fit_counts"] = {
                "attempted": attempted,
                "successful": successful,
                "failed": attempted - successful,
            }
            result["group_failure_fraction_per_dataset"] = scalar_summary(
                [
                    1
                    - record["group_summary"]["successful_groups"]
                    / record["group_summary"]["groups"]
                    for record in records
                ]
            )
        errors = [r["parameter_errors"] for r in passed if "parameter_errors" in r]
        if errors:
            if len(errors) != len(passed) or len({len(e) for e in errors}) != 1:
                raise ValueError("Inconsistent correct-family recovery scope")
            result["parameter_recovery_conditional_on_success"] = [
                {
                    "coordinate": i,
                    "bias": scalar_summary([e[i] for e in errors]),
                    "mse": scalar_summary([e[i] ** 2 for e in errors]),
                }
                for i in range(len(errors[0]))
            ]
        cohorts = set(configurations[key]["metric_schema"])
        if passed:
            expected_names = passed[0].get("parameter_error_names")
            if any(r.get("parameter_error_names") != expected_names for r in passed):
                raise ValueError("Changed estimated-coordinate recovery scope")
            if expected_names is not None:
                result["parameter_error_names"] = expected_names
            if any(set(r["future_metrics"]) != cohorts for r in passed):
                raise ValueError("Changed forecast cohorts")
        result["future_metrics"] = {}
        for cohort in sorted(cohorts):
            metrics = configurations[key]["metric_schema"][cohort]
            result["future_metrics"][cohort] = {}
            for name in metrics:
                if any(name not in r["future_metrics"][cohort] for r in passed):
                    raise ValueError("Changed predictive metric scope")
                values = [r["future_metrics"][cohort][name] for r in passed]
                summary = {
                    "conditional_on_success": scalar_summary(values)
                    if values
                    else {"count": 0, "mean": None, "mcse": None}
                }
                if "coverage" in name:
                    summary["procedural_over_all_attempts"] = scalar_summary(
                        [
                            r["future_metrics"][cohort][name] if r["status"] == "passed" else 0.0
                            for r in records
                        ]
                    )
                result["future_metrics"][cohort][name] = summary
        output.append(result)
    return {
        "schema_version": 1,
        "kind": "native020-monte-carlo-summary",
        "groups": output,
        "input_receipts": inputs,
        ("scope"): (
            "MCSE uses independent generated datasets, not rows or overlapping panel "
            "horizons. Failed fits remain in the attempted denominator. Small smoke "
            "repetition counts do not establish calibration, posterior inference or scale "
            "performance."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= len(args.reports) <= 10000:
        raise ValueError("Select1..10000bounded study shards")
    report = summarize(bounded_json(path) for path in args.reports)
    body = canonical(report) + b"\n"
    if len(body) > 4 * 1024 * 1024:
        raise ValueError("Summary exceeds4MiB; aggregate separate scopes")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(body)
    print(f"Summarized{len(report['groups'])}target/scenario/method groups")


if __name__ == "__main__":
    main()
