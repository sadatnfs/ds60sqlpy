# SPDX-License-Identifier: MIT
"""Pure deterministic mathematics and failure-accounting checks, no Spark/native."""

from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aggregate_extended import summarize
from extended_support import (
    close,
    named_oracle,
    panel_reference,
    penalty_value,
    prediction_metrics,
    row_moments,
    row_nll,
)
from generate_extended_fixtures import generate
from run_native_extended import admit_methods, fit_is_qualified, fit_options
from study_support import canonical, digest


class FixturesAndReferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = generate(replicates=2)

    def test_generation_is_deterministic_and_changed_replicates_differ(self):
        self.assertEqual(canonical(self.bundle), canonical(generate(replicates=2)))
        a, b = [
            c
            for c in self.bundle["cases"]
            if c["study"] == "sim-003" and c["scenario"] == "weak_slope"
        ]
        self.assertNotEqual(a["training"], b["training"])
        self.assertEqual(len(self.bundle["cases"]), 28)

    def test_training_and_future_are_bounded_and_disjoint(self):
        for case in self.bundle["cases"]:
            with self.subTest(study=case["study"], scenario=case["scenario"]):
                train = {r["row_id"] for r in case["training"]}
                future = {r["row_id"] for r in case["future"]}
                self.assertEqual(len(train), len(case["training"]))
                self.assertEqual(len(future), len(case["future"]))
                self.assertFalse(train & future)
                self.assertLessEqual(len(future), 128)
                self.assertLessEqual(len(train), 4096)

    def test_orthogonal_named_targets_and_fixed_nuisance(self):
        for case in self.bundle["cases"]:
            if case["study"] not in {"sim-003", "sim-004"}:
                continue
            for method in case["methods"]:
                oracle = named_oracle(case, method)
                self.assertLess(oracle["summed_kkt_inf"], 1e-12)
                self.assertEqual(oracle["parameters"][2], 0)
                self.assertEqual(method["fixed"], {"log_sigma": 0})
                options = fit_options(method, "weighted_mean", 32)
                if method["regularization"] and method["regularization"]["l1"]:
                    self.assertEqual(options["solver"]["initial_step"], 1)
                    self.assertEqual(options["solver"]["kkt_tolerance"], 1e-6)

    def test_known_exact_zero_lasso_and_nonzero_prior_center(self):
        case = {"training": [{"x": float(x), "y": 2 + 0.1 * x} for x in [-1, 1] * 4]}
        method = {"regularization": {"gaussian": {}, "l1": {"beta1": 4}}}
        self.assertEqual(named_oracle(case, method)["parameters"], [2, 0, 0])
        method = {
            "regularization": {
                "gaussian": {"beta1": {"mean": 0.2, "precision": 8}},
                "l1": {},
            }
        }
        close(named_oracle(case, method)["parameters"][1], 0.15, absolute=1e-14)

    def test_gaussian_prior_density_keeps_its_normalizing_constant(self):
        regularization = {
            "gaussian": {"beta1": {"mean": 0.2, "precision": 8}},
            "l1": {},
        }
        expected = 0.5 * (math.log(2 * math.pi) - math.log(8))
        close(
            penalty_value([2, 0.2, 0], ["beta0", "beta1", "log_sigma"], regularization),
            expected,
            absolute=1e-14,
        )
        self.assertLess(expected, 0)

    def test_preserved_study_ids(self):
        self.assertEqual(
            {case["study"] for case in self.bundle["cases"]},
            {
                "sim-003",
                "sim-004",
                "sim-009",
                "sim-020",
                "sim-022",
                "sim-024",
                "sim-028",
            },
        )

    def test_trial_generation_has_correct_integer_domain(self):
        for case in self.bundle["cases"]:
            if case["study"] != "sim-022":
                continue
            for row in case["training"] + case["future"]:
                self.assertTrue(row["y"].is_integer() and row["trials"].is_integer())
                self.assertTrue(0 <= row["y"] <= row["trials"])

    def test_count_densities_normalize_at_small_fixed_covariates(self):
        for model, theta in [
            ("poisson_exposure", [0.2, 0.4]),
            ("zero_inflated_poisson", [0.2, 0.4, -0.4, 0.6]),
            ("hurdle_poisson", [0.2, 0.4, -0.4, 0.6]),
        ]:
            row = {"x": 0.1, "z": -0.2, "exposure": 1.0}
            mass = math.fsum(
                math.exp(-row_nll(model, theta, row | {"y": float(y)})) for y in range(80)
            )
            self.assertAlmostEqual(mass, 1, places=13)
            distribution_mean = math.fsum(
                y * math.exp(-row_nll(model, theta, row | {"y": float(y)})) for y in range(80)
            )
            close(distribution_mean, row_moments(model, theta, row)[0], absolute=1e-12)

    def test_binomial_and_beta_binomial_normalize(self):
        for model, theta in [
            ("binomial_logistic", [0.2, 0.4]),
            ("beta_binomial", [0.2, 0.4, math.log(3)]),
        ]:
            row = {"x": 0.1, "trials": 8.0}
            mass = math.fsum(
                math.exp(-row_nll(model, theta, row | {"y": float(y)})) for y in range(9)
            )
            self.assertAlmostEqual(mass, 1, places=13)

    def test_robust_metric_does_not_label_gaussian_coverage(self):
        case = {"future": [{"row_id": 1, "x": 0.0, "y": 1.0}]}
        theta = [0, 0, 0, math.log(3)]
        metrics = prediction_metrics(
            case,
            "student_t_regression",
            theta,
            [{"row_id": 1, "mean": 0.0, "variance": 5 / 3}],
        )["future"]
        self.assertNotIn("gaussian_pointwise_coverage", metrics)
        close(
            metrics["mean_marginal_nll"],
            row_nll("student_t_regression", theta, case["future"][0]),
        )

    def test_panel_forecasts_are_forward_and_complete_group_conditioned(self):
        for case in self.bundle["cases"]:
            if case["study"] != "sim-028":
                continue
            self.assertEqual(len({r["unit"] for r in case["training"]}), 8)
            self.assertLess(
                max(r["x"] for r in case["training"]),
                min(r["x"] for r in case["future"]),
            )
            nll, predictions = panel_reference(
                case["truth"]["parameters"], case["training"], case["future"]
            )
            self.assertTrue(math.isfinite(nll))
            self.assertTrue(all(p["variance"] > 0 for p in predictions))
            self.assertEqual(len(predictions), 20)

    def test_constrained_stationarity_uses_correct_units(self):
        document = {
            "schema_version": 2,
            "fit": {"converged": True, "projected_gradient_inf": 99},
            "target": {
                "stationarity": {
                    "summed_inf": 1e-7,
                    "reduced_inf": 1e-9,
                    "tolerance": 1e-8,
                    "tolerance_units": "summed_target",
                }
            },
        }
        self.assertFalse(fit_is_qualified(document))
        document["target"]["stationarity"]["tolerance_units"] = "reduced_objective"
        self.assertTrue(fit_is_qualified(document))
        document["fit"]["converged"] = False
        self.assertFalse(fit_is_qualified(document))

    def test_method_and_dataset_admission_is_bounded(self):
        cases = [
            case
            for case in self.bundle["cases"]
            if case["study"] == "sim-003" and case["replicate"] == 0
        ]
        admit_methods(cases, "sim-003")
        for mutate in ("empty", "duplicate", "wrong_model", "changed_data"):
            changed = copy.deepcopy(cases)
            if mutate == "empty":
                changed[0]["methods"] = []
            elif mutate == "duplicate":
                changed[0]["methods"][1] = copy.deepcopy(changed[0]["methods"][0])
            elif mutate == "wrong_model":
                changed[0]["methods"][0]["model_id"] = "normal"
            else:
                changed[0]["training"][0]["y"] += 1
            with self.subTest(mutate=mutate), self.assertRaises(AssertionError):
                admit_methods(changed, "sim-003")

    def test_generator_refuses_invalid_bounds(self):
        for kwargs in [
            {"replicates": 0},
            {"replicates": True},
            {"seed": 2**53},
            {"seed": -1},
        ]:
            with self.assertRaises(ValueError):
                generate(**kwargs)


def synthetic_report(replicate=0, status="passed"):
    record = {
        "scenario": "a",
        "method": "m",
        "reduction": "sum",
        "case_sha256": str(replicate),
        "status": status,
        "target_configuration": {"fixed": {}},
        "metric_schema": {"future": ["mse", "gaussian_pointwise_coverage"]},
        "truth": {"parameters": [0]},
        "training_rows": 4,
        "future_rows": 2,
    }
    if status == "passed":
        record.update(
            {
                "parameter_errors": [float(replicate)],
                "future_metrics": {
                    "future": {
                        "rows": 2,
                        "mse": float(replicate + 1),
                        "gaussian_pointwise_coverage": 1.0,
                    }
                },
            }
        )
    return {
        "kind": "native020-actual-study",
        "status": "completed",
        "study": "sim-003",
        "seed": 1,
        "replicate": replicate,
        "dataset_identities": {
            "a": {
                "training_sha256": digest(["training", replicate]),
                "future_sha256": digest(["future", replicate]),
            }
        },
        "planned_records": [
            {k: record[k] for k in ["scenario", "method", "reduction", "case_sha256"]}
        ],
        "records": [record],
        "source_sha256": {"x": "a"},
        "generator_sha256": "g",
        "artifact_identity": {"build": "a"},
        "package_identity": {"version": "0.2.0"},
        "environment": {"machine": "arm64"},
        "partitions": 2,
    }


class MonteCarloAccounting(unittest.TestCase):
    def test_failure_denominator_and_independent_dataset_mcse(self):
        result = summarize([synthetic_report(0), synthetic_report(1, "failed")])["groups"][0]
        self.assertEqual(result["attempted_replications"], 2)
        self.assertEqual(result["successful_replications"], 1)
        metric = result["future_metrics"]["future"]["gaussian_pointwise_coverage"]
        self.assertEqual(metric["conditional_on_success"]["mean"], 1)
        self.assertEqual(metric["procedural_over_all_attempts"]["mean"], 0.5)
        self.assertAlmostEqual(metric["procedural_over_all_attempts"]["mcse"], 0.5)
        self.assertIsNone(metric["conditional_on_success"]["mcse"])

    def test_all_failed_coverage_keeps_procedural_denominator(self):
        result = summarize([synthetic_report(0, "failed"), synthetic_report(1, "failed")])[
            "groups"
        ][0]
        coverage = result["future_metrics"]["future"]["gaussian_pointwise_coverage"]
        self.assertEqual(
            coverage["procedural_over_all_attempts"], {"count": 2, "mean": 0.0, "mcse": 0.0}
        )
        self.assertEqual(
            coverage["conditional_on_success"], {"count": 0, "mean": None, "mcse": None}
        )
        self.assertNotIn("procedural_over_all_attempts", result["future_metrics"]["future"]["mse"])

    def test_duplicate_or_interrupted_shard_refused(self):
        report = synthetic_report()
        with self.assertRaises(ValueError):
            summarize([report, copy.deepcopy(report)])
        report["status"] = "interrupted"
        with self.assertRaises(ValueError):
            summarize([report])

    def test_missing_method_and_changed_target_refused(self):
        report = synthetic_report()
        report["records"] = []
        with self.assertRaises(ValueError):
            summarize([report])
        other = synthetic_report(1)
        other["records"][0]["target_configuration"] = {"fixed": {"scale": 1}}
        with self.assertRaises(ValueError):
            summarize([synthetic_report(), other])

    def test_relabelled_fixed_training_or_future_cannot_claim_dataset_mcse(self):
        original = synthetic_report(0)
        for split in ("training_sha256", "future_sha256"):
            relabelled = synthetic_report(1)
            relabelled["dataset_identities"]["a"][split] = original["dataset_identities"]["a"][
                split
            ]
            with (
                self.subTest(split=split),
                self.assertRaisesRegex(ValueError, "Repeated training or future"),
            ):
                summarize([original, relabelled])

    def test_source_artifact_environment_change_refused(self):
        for key in ["source_sha256", "artifact_identity", "environment"]:
            other = synthetic_report(1)
            other[key] = {"changed": True}
            with self.subTest(key=key), self.assertRaises(ValueError):
                summarize([synthetic_report(), other])


if __name__ == "__main__":
    unittest.main()
