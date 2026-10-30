"""Compare completed paired study shards without hiding failed fits or target differences."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from study_support import bounded_json, canonical, digest


def compare(native: dict[str, Any], torch: dict[str, Any]) -> dict[str, Any]:
    for result, backend in ((native, "native"), (torch, "torch")):
        if (
            result.get("kind") != "original-spark-modeling-study"
            or result.get("status") != "completed"
            or result.get("backend") != backend
        ):
            raise ValueError(
                "Compare only completed actual study shards from the selected backends"
            )
    for key in (
        "study",
        "replicate",
        "seed",
        "fixture_sha256",
        "generator_sha256",
        "study_source_sha256",
    ):
        if native[key] != torch[key]:
            raise ValueError("Study inputs, replication or reference source differ: " + key)

    def records(report):
        result = {}
        for row in report["records"]:
            key = (row["scenario"], row["method"])
            if key in result:
                raise ValueError("Duplicate scenario/method record")
            result[key] = row
        return result

    left, right = records(native), records(torch)
    if set(left) != set(right):
        raise ValueError("Paired method/scenario coverage differs")
    result = []
    for key in sorted(left):
        a, b = left[key], right[key]
        for name in (
            "case_sha256",
            "truth",
            "canonical_initial",
            "l2_strength",
            "training_rows",
            "future_rows",
        ):
            if a[name] != b[name]:
                raise ValueError("Paired scientific target/configuration differs: " + name)
        row = {
            "scenario": key[0],
            "method": key[1],
            "native_status": a["status"],
            "torch_status": b["status"],
        }
        if a["status"] == "passed" and b["status"] == "passed":
            row.update(
                parameter_absolute_differences=[
                    abs(x - y) for x, y in zip(a["parameters"], b["parameters"], strict=True)
                ],
                objective_absolute_difference=abs(
                    a["canonical_reference_objective"] - b["canonical_reference_objective"]
                ),
                native_prediction_scope=a["prediction_scope"],
                torch_prediction_scope=b["prediction_scope"],
                native_canonical_score=a["canonical_projected_score_inf"],
                torch_canonical_score=b["canonical_projected_score_inf"],
            )
        else:
            row["comparison"] = "No successful-fit parity claim; failed attempts remain visible"
        result.append(row)
    return {
        "schema_version": 1,
        "kind": "paired-modeling-study-comparison",
        "status": "completed",
        "study": native["study"],
        "replicate": native["replicate"],
        "fixture_sha256": native["fixture_sha256"],
        "records": result,
        "native_report_sha256": digest(native),
        "torch_report_sha256": digest(torch),
        "partitions": {"native": native["partitions"], "torch": torch["partitions"]},
        "package_identities": {
            "native": native["package_identity"],
            "torch": torch["package_identity"],
        },
        "scope": (
            "comparison of observed fitted states; differing nonlinear fits can reflect "
            "weak identification or separate stationary points, "
            "not automatically a runtime regression"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--torch", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Keep earlier evidence; select a new output file")
    result = compare(bounded_json(args.native), bounded_json(args.torch))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        f.write(canonical(result) + b"\n")
    print(
        canonical(
            {
                "status": "completed",
                "study": result["study"],
                "records": len(result["records"]),
                "path": str(args.output),
            }
        ).decode()
    )


if __name__ == "__main__":
    main()
