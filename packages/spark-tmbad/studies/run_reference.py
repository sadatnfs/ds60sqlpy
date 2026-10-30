"""Original exact reference studies; this does not execute either Spark package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
from pathlib import Path

from study_support import (
    Z95,
    aggregate,
    canonical,
    gamma_poisson_posterior,
    normal,
    normal_posterior,
    orthogonal_estimate,
    scalar_summary,
    wilson,
)


def regularization(seed: int, replicates: int) -> list[dict]:
    n = 32
    design = [
        [1.0 if (i & mask).bit_count() % 2 == 0 else -1.0 for mask in (0, 1, 2, 4)]
        for i in range(n)
    ]
    output = []
    for scenario, truth in [("strong", [0.5, 1.2, 0.0, -0.8]), ("weak", [0.5, 0.1, 0.0, -0.1])]:
        methods = {name: [] for name in ("none", "ridge", "lasso")}
        for replicate in range(replicates):
            response = [
                math.fsum(x * b for x, b in zip(row, truth, strict=True))
                + normal(seed, "orthogonal", replicate, i)
                for i, row in enumerate(design)
            ]
            fixture_hash = hashlib.sha256(
                canonical({"design": design, "response": response})
            ).hexdigest()
            for method in methods:
                result = orthogonal_estimate(
                    design, response, 1.0, 8.0, method, [False, True, True, True]
                )
                if result["kkt_residual_inf"] > 1e-10:
                    raise AssertionError("Exact reference violates KKT conditions")
                methods[method].append(
                    {
                        "status": "passed",
                        "replicate": replicate,
                        "fixture_sha256": fixture_hash,
                        **result,
                    }
                )
        output.append(
            {
                "study": "orthogonal_ridge_lasso",
                "scenario": scenario,
                "truth": truth,
                "known_sigma": 1.0,
                "penalty_strength": 8.0,
                "intercept_penalized": False,
                "methods": {
                    name: {"summary": aggregate(values, truth), "records": values}
                    for name, values in methods.items()
                },
            }
        )
    return output


def posterior_study(seed: int, replicates: int) -> list[dict]:
    n = 12
    sigma = 1.0
    prior_mean = 0.0
    prior_sd = 0.5
    output = []
    for regime in ("fixed_truth", "prior_predictive"):
        records = []
        for r in range(replicates):
            truth = (
                2.0
                if regime == "fixed_truth"
                else prior_mean + prior_sd * normal(seed, "posterior", "truth", r)
            )
            observed = [truth + sigma * normal(seed, "posterior", "noise", r, i) for i in range(n)]
            posterior = normal_posterior(observed, sigma, prior_mean, prior_sd)
            standardized = (truth - posterior["mean"]) / math.sqrt(posterior["variance"])
            records.append(
                {
                    "replicate": r,
                    "truth": truth,
                    "posterior": posterior,
                    "covered": abs(standardized) <= Z95,
                    "truth_posterior_cdf": 0.5 * (1 + math.erf(standardized / math.sqrt(2))),
                    "error": posterior["mean"] - truth,
                }
            )
        output.append(
            {
                "study": "exact_normal_posterior",
                "truth_regime": regime,
                "records": records,
                "coverage": wilson(sum(x["covered"] for x in records), len(records)),
                "posterior_mean_error": scalar_summary([x["error"] for x in records]),
                "target": (
                    "exact conjugate posterior; this does not imply a generic package sampler"
                ),
            }
        )
    cases = []
    for label, counts, exposures, a, b in [
        ("interior", [1, 1, 1], [0.5, 0.5, 1.0], 2.0, 1.0),
        ("boundary", [0, 0], [1.0, 1.0], 0.4, 1.0),
    ]:
        posterior = gamma_poisson_posterior(counts, exposures, a, b)
        rng = random.Random(
            int.from_bytes(
                hashlib.sha256(canonical([seed, label, "posterior_draws"])).digest()[:16], "big"
            )
        )
        draws = [rng.gammavariate(posterior["shape"], 1 / posterior["rate"]) for _ in range(512)]
        summary = scalar_summary(draws)
        cases.append(
            {
                "case": label,
                "posterior": posterior,
                "independent_exact_posterior_draws": 512,
                "draw_mean": summary,
                "draw_mean_theoretical_mcse": math.sqrt(posterior["variance"] / 512),
                "sampling_scope": (
                    "stdlib Gamma draws from the exact conjugate law; "
                    "not MCMC or a package posterior feature"
                ),
            }
        )
    output.append({"study": "gamma_poisson_coordinate_modes", "cases": cases})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--replicates", type=int, default=8)
    parser.add_argument("--seed", type=int, default=61029)
    parser.add_argument("--preset", choices=["smoke", "monte-carlo"], default="smoke")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output path; earlier study receipts are retained")
    if not 2 <= args.replicates <= 10000:
        raise ValueError("Choose 2..10000 independent reference replications")
    if args.preset == "smoke" and args.replicates > 16:
        raise ValueError("More than 16 replications needs explicit monte-carlo preset")
    report = {
        "schema_version": 1,
        "kind": "original-modeling-reference-studies",
        "status": "passed",
        "execution": (
            "standard-library exact mathematical references only; "
            "no Spark/native/Torch backend execution"
        ),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "preset": args.preset,
        "seed": args.seed,
        "replicates": args.replicates,
        "coverage_claim": (
            "smoke gives code evidence only; retain MCSE and uncertainty for larger runs"
        ),
        "source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("run_reference.py", "study_support.py")
        },
        "studies": regularization(args.seed, args.replicates)
        + posterior_study(args.seed, args.replicates),
    }
    body = canonical(report) + b"\n"
    if len(body) > 64 * 1024 * 1024:
        raise ValueError("Reference report exceeds 64 MiB; shard the study")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        f.write(body)
    print(
        json.dumps(
            {
                "status": "passed",
                "scope": report["execution"],
                "path": str(args.output),
                "replicates": args.replicates,
                "sha256": hashlib.sha256(body).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
