# SPDX-License-Identifier: MIT
"""Original bounded native0.2 synthetic studies, separate from historical fixtures."""

from __future__ import annotations

import argparse
import hashlib
import math
import random
from pathlib import Path

from study_support import canonical, digest, normal, uniform


def rng(seed, *key):
    return random.Random(int.from_bytes(hashlib.sha256(canonical([seed, *key])).digest(), "big"))


def poisson(generator, mean):
    if not 0 < mean < 50:
        raise ValueError("Small study Poisson sampler requires rate in (0,50)")
    product, count = 1.0, 0
    bound = math.exp(-mean)
    while product > bound:
        product *= generator.random()
        count += 1
        if count > 10000:
            raise RuntimeError("Bounded count sampler exceeded its budget")
    return count - 1


def method(name, model, initial, **extra):
    return {
        "id": name,
        "model_id": model,
        "initial": initial,
        "fixed": {},
        "regularization": None,
        **extra,
    }


def add_case(cases, study, scenario, replicate, training, future, methods, truth, scope):
    cases.append(
        {
            "study": study,
            "scenario": scenario,
            "replicate": replicate,
            "training": training,
            "future": future,
            "training_sha256": digest(training),
            "future_sha256": digest(future),
            "methods": methods,
            "truth": truth,
            "scope": scope,
        }
    )


def generate(seed=381729, replicates=2):
    if (
        type(seed) is not int
        or not 0 <= seed < 2**53
        or type(replicates) is not int
        or not 1 <= replicates <= 100
    ):
        raise ValueError("Use an exact nonnegative seed and1..100replications")
    cases = []
    for replicate in range(replicates):
        for scenario, slope in [("weak_slope", 0.15), ("strong_slope", 1.2)]:
            training, future = [], []
            for split, count, output in [
                ("train", 32, training),
                ("future", 24, future),
            ]:
                for i in range(count):
                    x = float(-1 if i % 2 else 1)
                    output.append(
                        {
                            "row_id": i if split == "train" else 1000 + i,
                            "x": x,
                            "y": 2
                            + slope * x
                            + normal(seed, "named", replicate, scenario, split, i),
                        }
                    )
            baseline = method("unpenalized", "linear_gaussian", [0, 0, 0], fixed={"log_sigma": 0})
            for study, kind, penalty in [
                (
                    "sim-003",
                    "selected_gaussian",
                    {"gaussian": {"beta1": {"mean": 0.2, "precision": 8}}, "l1": {}},
                ),
                ("sim-004", "selected_l1", {"gaussian": {}, "l1": {"beta1": 4}}),
            ]:
                regularization = {
                    "schema_version": 1,
                    "coordinate_system": "native_optimizer_parameters",
                    "normalization": "summed_likelihood_target",
                    **penalty,
                }
                methods = [
                    baseline,
                    method(
                        kind,
                        "linear_gaussian",
                        [0, 0, 0],
                        fixed={"log_sigma": 0},
                        regularization=regularization,
                    ),
                ]
                add_case(
                    cases,
                    study,
                    scenario,
                    replicate,
                    training,
                    future,
                    methods,
                    {"model_id": "linear_gaussian", "parameters": [2, slope, 0]},
                    (
                        "Independent Gaussian rows, orthogonal [1,x], known sigma1. Intercept"
                        " is unpenalized. Compare sum and weighted_mean at the identical "
                        "summed target; no posterior sampling."
                    ),
                )
        for scenario, overdispersed in [
            ("binomial_truth", False),
            ("beta_binomial_truth", True),
        ]:
            training, future = [], []
            for split, count, output in [
                ("train", 64, training),
                ("future", 24, future),
            ]:
                for i in range(count):
                    x = 2 * uniform(seed, "trials", replicate, split, "x", i) - 1
                    probability = 1 / (1 + math.exp(-(-0.4 + 0.8 * x)))
                    generator = rng(seed, "trials", replicate, scenario, split, i)
                    p = (
                        generator.betavariate(probability * 3, (1 - probability) * 3)
                        if overdispersed
                        else probability
                    )
                    trials = 8 + i % 5
                    output.append(
                        {
                            "row_id": i if split == "train" else 1000 + i,
                            "x": x,
                            "trials": float(trials),
                            "y": float(sum(generator.random() < p for _ in range(trials))),
                        }
                    )
            methods = [
                method("binomial", "binomial_logistic", [0, 0]),
                method("beta_binomial", "beta_binomial", [0, 0, math.log(5)]),
            ]
            truth = {
                "model_id": "beta_binomial" if overdispersed else "binomial_logistic",
                "parameters": [-0.4, 0.8, math.log(3)] if overdispersed else [-0.4, 0.8],
            }
            add_case(
                cases,
                "sim-022",
                scenario,
                replicate,
                training,
                future,
                methods,
                truth,
                (
                    "Independent trial counts; beta-binomial latent probabilities are redrawn"
                    " for every observation. The binomial limit is not a finite beta-binomial"
                    " precision truth. Report correct-model recovery separately from "
                    "misspecification."
                ),
            )
        for scenario, inflated in [
            ("poisson_truth", False),
            ("structural_zero_truth", True),
        ]:
            training, future = [], []
            for split, count, output in [
                ("train", 96, training),
                ("future", 24, future),
            ]:
                for i in range(count):
                    x = 2 * uniform(seed, "zeros", replicate, split, "x", i) - 1
                    z = 2 * uniform(seed, "zeros", replicate, split, "z", i) - 1
                    exposure = [0.5, 1.0, 2.0][i % 3]
                    generator = rng(seed, "zeros", replicate, scenario, split, i)
                    zero_probability = 1 / (1 + math.exp(-(-0.4 + 0.6 * z))) if inflated else 0
                    y = (
                        0
                        if generator.random() < zero_probability
                        else poisson(generator, exposure * math.exp(0.2 + 0.4 * x))
                    )
                    output.append(
                        {
                            "row_id": i if split == "train" else 1000 + i,
                            "x": x,
                            "z": z,
                            "exposure": exposure,
                            "y": float(y),
                        }
                    )
            methods = [
                method("poisson", "poisson_exposure", [0, 0]),
                method("zero_inflated", "zero_inflated_poisson", [0, 0, 0, 0]),
                method("hurdle", "hurdle_poisson", [0, 0, 0, 0]),
            ]
            truth = {
                "model_id": "zero_inflated_poisson" if inflated else "poisson_exposure",
                "parameters": [0.2, 0.4, -0.4, 0.6] if inflated else [0.2, 0.4],
            }
            add_case(
                cases,
                "sim-020",
                scenario,
                replicate,
                training,
                future,
                methods,
                truth,
                (
                    "Independent exposure counts. Structural zeros and sampling zeros are "
                    "distinct. Hurdle zero probability depends on z only; it need not "
                    "represent the ZIP zero probability, which also depends on x and "
                    "exposure. No boundary ZIP truth is fabricated for ordinary Poisson data."
                ),
            )
        for scenario, contaminated in [
            ("gaussian_truth", False),
            ("symmetric_contamination", True),
        ]:
            training, future = [], []
            for split, count, output in [
                ("train", 64, training),
                ("future", 24, future),
            ]:
                for i in range(count):
                    x = 2 * uniform(seed, "robust", replicate, split, "x", i) - 1
                    error = normal(seed, "robust", replicate, split, "noise", i)
                    if (
                        contaminated
                        and uniform(seed, "robust", replicate, split, "contamination", i) < 0.1
                    ):
                        error *= 8
                    output.append(
                        {
                            "row_id": i if split == "train" else 1000 + i,
                            "x": x,
                            "y": 0.5 + 0.8 * x + error,
                        }
                    )
            methods = [
                method("gaussian", "linear_gaussian", [0, 0, 0]),
                method(
                    "student_t_df5",
                    "student_t_regression",
                    [0, 0, 0, math.log(3)],
                    fixed={"log_df_minus_two": math.log(3)},
                ),
            ]
            truth = {
                "model_id": None if contaminated else "linear_gaussian",
                "parameters": [0.5, 0.8, 0] if not contaminated else None,
                "conditional_mean_coefficients": [0.5, 0.8],
                "contamination_probability": 0.1 if contaminated else 0,
            }
            add_case(
                cases,
                "sim-024",
                scenario,
                replicate,
                training,
                future,
                methods,
                truth,
                (
                    "Independent continuous outcomes; symmetric contamination is a Gaussian "
                    "scale mixture, not exactly Student-t. Student-t degrees of freedom are "
                    "fixed to5 while scale is fitted. Use each fitted density for heldout "
                    "score; Gaussian bands are not Student-t calibration."
                ),
            )
        for scenario, rho in [
            ("positive_correlation", 0.65),
            ("negative_correlation", -0.65),
        ]:
            training, future = [], []
            truth = [
                0.8,
                0.4,
                math.log(0.35),
                math.log(0.7),
                math.log(0.3),
                math.atanh(rho),
            ]
            for g in range(10):
                a = normal(seed, "panel", replicate, scenario, "latent0", g)
                b = normal(seed, "panel", replicate, scenario, "latent1", g)
                u0 = 0.7 * a
                u1 = 0.3 * (rho * a + math.sqrt(1 - rho * rho) * b)
                for split, xs, output in [
                    ("train", [-1, -0.6, -0.2, 0.2, 0.6, 1], training),
                    ("future", [1.5, 2], future),
                ]:
                    if g >= 8 and split == "train":
                        continue
                    for i, x in enumerate(xs):
                        output.append(
                            {
                                "row_id": g * 10 + i if split == "train" else 1000 + g * 10 + i,
                                "unit": f"u{g}",
                                "x": float(x),
                                "y": 0.8
                                + 0.4 * x
                                + u0
                                + u1 * x
                                + 0.35 * normal(seed, "panel", replicate, scenario, split, g, i),
                                "cohort": "known" if g < 8 else "unseen",
                            }
                        )
            fixed = dict(
                zip(
                    ["log_sigma", "log_tau0", "log_tau1", "atanh_correlation"],
                    truth[2:],
                    strict=True,
                )
            )
            methods = [
                method(
                    "known_covariance",
                    "gaussian_correlated_random_slope",
                    [0, 0, *truth[2:]],
                    fixed=fixed,
                ),
                method(
                    "estimated_covariance",
                    "gaussian_correlated_random_slope",
                    [0, 0, math.log(0.5), math.log(0.6), math.log(0.4), 0],
                ),
            ]
            add_case(
                cases,
                "sim-028",
                scenario,
                replicate,
                training,
                future,
                methods,
                {"model_id": "gaussian_correlated_random_slope", "parameters": truth},
                (
                    "Eight independent complete Gaussian panels fit one shared population "
                    "vector. Known/unseen forecast groups reuse/newly draw latent effects. "
                    "Training x<=1, future x>=1.5. Covariance-known and covariance-estimated "
                    "methods are separate; plug-in bands omit population-parameter "
                    "uncertainty."
                ),
            )
        for scenario, heterogeneity in [
            ("equal_group_means", 0.0),
            ("heterogeneous_group_means", 1.5),
        ]:
            training, future = [], []
            group_truth = {}
            for g in range(4):
                location = 0.5 + heterogeneity * (g - 1.5)
                group_truth[f"u{g}"] = [location, 0]
                for split, count, output in [
                    ("train", 16, training),
                    ("future", 4, future),
                ]:
                    for i in range(count):
                        output.append(
                            {
                                "row_id": g * 100 + i if split == "train" else 1000 + g * 100 + i,
                                "unit": f"u{g}",
                                "y": location
                                + normal(
                                    seed,
                                    "independent",
                                    replicate,
                                    scenario,
                                    split,
                                    g,
                                    i,
                                ),
                            }
                        )
            methods = [
                method("pooled_shared", "normal", [0, 0]),
                method(
                    "independent_groups",
                    "normal",
                    [0, 0],
                    mechanism="independent_groups",
                ),
            ]
            add_case(
                cases,
                "sim-009",
                scenario,
                replicate,
                training,
                future,
                methods,
                {
                    "model_id": "normal",
                    "parameters": None,
                    "group_parameters": group_truth,
                },
                (
                    "Each independent group estimates its own parameter vector. No "
                    "latent-effect marginalization is implied. Group model documents remain "
                    "distributed; only bounded aggregate diagnostics and requested future "
                    "rows reach the driver."
                ),
            )
    return {
        "schema_version": 1,
        "kind": "native020-study-fixtures",
        "seed": seed,
        "replicates_per_scenario": replicates,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        ("randomness"): (
            "SHA256-keyed52-bit uniforms/Box-Muller normals and separately keyed Python "
            "Random for bounded Bernoulli/beta/Poisson draws; retained fixture bytes are "
            "authoritative across environments"
        ),
        "scope": "Original synthetic smoke/study inputs. No runtime or Monte Carlo conclusion.",
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=381729)
    parser.add_argument("--replicates", type=int, default=2)
    args = parser.parse_args()
    bundle = generate(args.seed, args.replicates)
    body = canonical(bundle) + b"\n"
    if len(body) > 4 * 1024 * 1024:
        raise ValueError("Fixture exceeds4MiB; create separate batches")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(body)
    print(f"Wrote{len(bundle['cases'])}study cases")


if __name__ == "__main__":
    main()
