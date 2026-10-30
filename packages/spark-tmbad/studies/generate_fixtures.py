"""Generate bounded original shared study data; never execute a fit or download data."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

from study_support import canonical, normal, uniform


def generate(seed: int = 61029, replicates: int = 2) -> dict:
    if (
        type(seed) is not int
        or not 0 <= seed < 2**63
        or type(replicates) is not int
        or not 1 <= replicates <= 16
    ):
        raise ValueError(
            "Fixture bundles require seed>=0 and 1..16 replicates; shard larger studies"
        )
    cases = []
    for replicate in range(replicates):
        for scenario, weighted in [("ordinary", False), ("unequal_weights", True)]:
            rows = []
            for i in range(48):
                y = 1.2 + 0.7 * normal(seed, "normal", replicate, "train", i)
                rows.append({"row_id": i, "y": y, "weight": float(i % 4) if weighted else 1.0})
            future = [
                {
                    "row_id": 1000 + i,
                    "y": 1.2 + 0.7 * normal(seed, "normal", replicate, "future", i),
                }
                for i in range(16)
            ]
            cases.append(
                {
                    "study": "sim-001",
                    "case": "normal_mle",
                    "scenario": scenario,
                    "replicate": replicate,
                    "truth": [1.2, math.log(0.7)],
                    "initial": [0.0, 0.0],
                    "training": rows,
                    "future": future,
                    "methods": [{"id": "unpenalized", "l2_strength": 0.0}],
                    "weight_interpretation": (
                        "fixed objective weights on independent original rows; "
                        "naive frequency uncertainty is deliberately contrasted"
                    )
                    if weighted
                    else "independent equally weighted observations",
                }
            )
        for scenario, beta0, sigma in [("centered", 0.0, 1.0), ("offset_and_scale", 4.0, 2.0)]:
            rows = []
            future = []
            for split, count, target in [("train", 64, rows), ("future", 24, future)]:
                for i in range(count):
                    x = 2 * uniform(seed, "linear", replicate, split, "x", i) - 1
                    y = (
                        beta0
                        + 1.2 * x
                        + sigma * normal(seed, "linear", replicate, split, "noise", i)
                    )
                    target.append(
                        {"row_id": i if split == "train" else 1000 + i, "one": 1.0, "x": x, "y": y}
                    )
            cases.append(
                {
                    "study": "sim-002",
                    "case": "linear_all_coordinate_map",
                    "scenario": scenario,
                    "replicate": replicate,
                    "truth": [beta0, 1.2, math.log(sigma)],
                    "initial": [0.0, 0.0, 0.0],
                    "training": rows,
                    "future": future,
                    "methods": [
                        {"id": "unpenalized", "l2_strength": 0.0},
                        {"id": "all_coordinate_l2", "l2_strength": 4.0},
                    ],
                    "prior_measure": (
                        "Gaussian prior on beta0,beta1,log_sigma coordinates; "
                        "this is not slope-only ridge"
                    ),
                }
            )
        for scenario, last in [("observed_curve", 4.0), ("short_prefix", 0.6)]:
            rows = []
            future = []
            for i in range(40):
                time = last * i / 39
                y = (
                    0.4
                    - 2 * math.expm1(-0.5 * time)
                    + 0.25 * normal(seed, "growth", replicate, "train", i)
                )
                rows.append({"row_id": i, "time": time, "y": y})
            for i in range(16):
                time = last + 0.15 + 2 * i / 15
                y = (
                    0.4
                    - 2 * math.expm1(-0.5 * time)
                    + 0.25 * normal(seed, "growth", replicate, "future", i)
                )
                future.append({"row_id": 1000 + i, "time": time, "y": y})
            cases.append(
                {
                    "study": "sim-006",
                    "case": "nonlinear_growth",
                    "scenario": scenario,
                    "replicate": replicate,
                    "truth": [0.4, math.log(2), math.log(0.5), math.log(0.25)],
                    "initial": [0.0, math.log(1.8), math.log(0.4), math.log(0.4)],
                    "training": rows,
                    "future": future,
                    "methods": [{"id": "unpenalized", "l2_strength": 0.0}],
                    "torch_coordinate_map": (
                        "amplitude=-exp(log_amplitude), offset=baseline+exp(log_amplitude); "
                        "no penalty equivalence assumed"
                    ),
                }
            )
        for scenario in ["balanced", "unequal_group_sizes"]:
            rows = []
            future = []
            row_id = 0
            for g in range(8):
                count = 6 if scenario == "balanced" else 3 + g
                latent = 0.9 * normal(seed, "groups", replicate, "latent", g)
                for i in range(count):
                    rows.append(
                        {
                            "row_id": row_id,
                            "unit": f"u{g}",
                            "y": 0.7
                            + latent
                            + 0.4 * normal(seed, "groups", replicate, "train", g, i),
                        }
                    )
                    row_id += 1
                for i in range(2):
                    future.append(
                        {
                            "row_id": 1000 + 2 * g + i,
                            "unit": f"u{g}",
                            "cohort": "known",
                            "y": 0.7
                            + latent
                            + 0.4 * normal(seed, "groups", replicate, "future", g, i),
                        }
                    )
            for g in range(2):
                latent = 0.9 * normal(seed, "groups", replicate, "new_latent", g)
                for i in range(2):
                    future.append(
                        {
                            "row_id": 2000 + 2 * g + i,
                            "unit": f"new{g}",
                            "cohort": "unseen",
                            "y": 0.7
                            + latent
                            + 0.4 * normal(seed, "groups", replicate, "new_future", g, i),
                        }
                    )
            cases.append(
                {
                    "study": "sim-008",
                    "case": "random_intercept",
                    "scenario": scenario,
                    "replicate": replicate,
                    "truth": [0.7, math.log(0.4), math.log(0.9)],
                    "initial": [0.0, math.log(0.6), math.log(0.8)],
                    "training": rows,
                    "future": future,
                    "methods": [{"id": "unpenalized", "l2_strength": 0.0}],
                    "independence": (
                        "complete independent groups; "
                        "future known groups reuse the generating latent effect"
                    ),
                }
            )
    return {
        "schema_version": 1,
        "kind": "original-shared-modeling-fixtures",
        "seed": seed,
        "replicates_per_scenario": replicates,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "randomness": (
            "SHA256-keyed 52-bit open uniforms and Box-Muller normals; "
            "retain exact fixture bytes across platforms"
        ),
        "scope": "small synthetic CPU study fixtures, not a scientific Monte Carlo conclusion",
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=61029)
    parser.add_argument("--replicates", type=int, default=2)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    body = canonical(generate(args.seed, args.replicates)) + b"\n"
    if len(body) > 4 * 1024 * 1024:
        raise ValueError("Fixture bundle exceeds 4 MiB; shard by replication")
    if args.check:
        if args.output.read_bytes() != body:
            raise SystemExit("Fixture bytes differ from this generator/environment")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(body)
    print(
        json.dumps(
            {
                "source_only": True,
                "python_version": platform.python_version(),
                "path": str(args.output),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
