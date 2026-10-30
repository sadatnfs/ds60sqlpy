"""Meaningful small mathematical/fixture tests; no Spark acceptance is implied."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generate_fixtures import generate
from study_support import (
    aggregate,
    canonical,
    forecast_metrics,
    gamma_poisson_posterior,
    normal_posterior,
    objective,
    orthogonal_estimate,
    paired_summary,
    prediction_reference,
    uniform,
    wilson,
)


class FixtureTests(unittest.TestCase):
    def test_keyed_streams_do_not_depend_on_generation_order(self):
        values = [uniform(19, "train", i) for i in range(10)]
        self.assertTrue(all(0 < x < 1 for x in values))
        for i in reversed(range(10)):
            self.assertEqual(uniform(19, "train", i), values[i])
        self.assertNotEqual(values, [uniform(19, "future", i) for i in range(10)])

    def test_shared_fixtures_preserve_splits_and_known_group_latents(self):
        bundle = generate(123, 1)
        self.assertEqual(len(bundle["cases"]), 8)
        self.assertEqual(canonical(bundle), canonical(generate(123, 1)))
        for case in bundle["cases"]:
            train = {x["row_id"] for x in case["training"]}
            future = {x["row_id"] for x in case["future"]}
            self.assertFalse(train & future)
            self.assertEqual(len(train), len(case["training"]))
            self.assertEqual(len(future), len(case["future"]))
        normals = [x for x in bundle["cases"] if x["case"] == "normal_mle"]
        self.assertEqual(
            [x["y"] for x in normals[0]["training"]], [x["y"] for x in normals[1]["training"]]
        )
        group = next(x for x in bundle["cases"] if x["case"] == "random_intercept")
        known = {x["unit"] for x in group["training"]}
        self.assertTrue(
            all((x["unit"] in known) == (x["cohort"] == "known") for x in group["future"])
        )

    def test_seed_and_replication_limits(self):
        for args in [(True, 1), (1, 0), (1, 17), (-1, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                generate(*args)


class MathematicalTests(unittest.TestCase):
    def test_exact_lasso_and_ridge_differ_and_satisfy_kkt(self):
        design = [[1.0, 1.0], [1.0, -1.0], [1.0, 1.0], [1.0, -1.0]]
        response = [1.2, 0.8, 1.2, 0.8]
        ols = orthogonal_estimate(design, response, 1.0, 1.0, "none", [False, True])
        ridge = orthogonal_estimate(design, response, 1.0, 1.0, "ridge", [False, True])
        lasso = orthogonal_estimate(design, response, 1.0, 1.0, "lasso", [False, True])
        self.assertAlmostEqual(ols["parameters"][1], 0.2)
        self.assertAlmostEqual(ridge["parameters"][1], 0.16)
        self.assertEqual(lasso["parameters"][1], 0.0)
        for result in (ols, ridge, lasso):
            self.assertEqual(result["parameters"][0], 1.0)
            self.assertLess(result["kkt_residual_inf"], 1e-12)
        with self.assertRaises(ValueError):
            orthogonal_estimate(
                [[1.0, 1.0], [1.0, 2.0]], [1.0, 2.0], 1.0, 1.0, "lasso", [False, True]
            )
        with self.assertRaises(ValueError):
            orthogonal_estimate(design, response, float("nan"), 1.0, "ridge", [False, True])

    def test_conjugate_posterior_target_and_coordinate_modes(self):
        normal = normal_posterior([1.0, 2.0, 3.0], 1.0, 0.0, 1.0)
        self.assertEqual(normal["mean"], 1.5)
        self.assertEqual(normal["variance"], 0.25)
        self.assertEqual(normal["predictive_variance"], 1.25)
        gamma = gamma_poisson_posterior([1, 1, 1], [0.5, 0.5, 1.0], 2.0, 1.0)
        self.assertEqual(gamma["shape"], 5.0)
        self.assertEqual(gamma["rate"], 3.0)
        self.assertAlmostEqual(gamma["natural_coordinate_interior_map"], 4 / 3)
        self.assertAlmostEqual(gamma["log_coordinate_map_mapped_to_rate"], 5 / 3)
        self.assertGreater(gamma["unit_exposure_predictive_variance"], gamma["mean"])
        boundary = gamma_poisson_posterior([0], [1.0], 0.4, 1.0)
        self.assertIsNone(boundary["natural_coordinate_interior_map"])
        self.assertEqual(boundary["natural_coordinate_boundary_supremum"], 0.0)
        with self.assertRaises(ValueError):
            normal_posterior([1.0], 1.0, 0.0, math.inf)
        with self.assertRaises(ValueError):
            gamma_poisson_posterior([True], [1.0], 1.0, 1.0)

    def test_analytic_scores_against_two_numerical_steps(self):
        for case in generate(22, 1)["cases"]:
            theta = case["truth"]
            for strength in [0.0, 0.4] if case["case"] != "nonlinear_growth" else [0.0]:
                value, gradient = objective(case, theta, strength)
                self.assertTrue(math.isfinite(value))
                for step in (1e-4, 1e-5):
                    for j in range(len(theta)):
                        plus, minus = theta.copy(), theta.copy()
                        plus[j] += step
                        minus[j] -= step
                        derivative = (
                            objective(case, plus, strength)[0] - objective(case, minus, strength)[0]
                        ) / (2 * step)
                        self.assertAlmostEqual(derivative, gradient[j], delta=2e-5)

    def test_group_density_against_independent_two_by_two_inverse(self):
        case = {
            "case": "random_intercept",
            "training": [{"unit": "a", "y": 1.0}, {"unit": "a", "y": 3.0}],
        }
        theta = [0.4, math.log(0.7), math.log(0.9)]
        s, t = 0.7**2, 0.9**2
        det = s * (s + 2 * t)
        a, b = 1.0 - theta[0], 3.0 - theta[0]
        direct = 0.5 * (
            2 * math.log(2 * math.pi)
            + math.log(det)
            + ((s + t) * (a * a + b * b) - 2 * t * a * b) / det
        )
        self.assertAlmostEqual(objective(case, theta)[0], direct, places=12)

    def test_known_unseen_group_moments_and_path_coverage(self):
        case = {
            "case": "random_intercept",
            "training": [{"unit": "a", "y": 2.0}, {"unit": "a", "y": 4.0}],
            "future": [
                {"row_id": 10, "unit": "a", "cohort": "known", "y": 3.0},
                {"row_id": 11, "unit": "a", "cohort": "known", "y": 20.0},
                {"row_id": 12, "unit": "new", "cohort": "unseen", "y": 1.0},
            ],
        }
        prediction = prediction_reference(case, [1.0, 0.0, 0.0])
        self.assertAlmostEqual(prediction[0]["mean"], 1.0 + 4 / 3)
        self.assertAlmostEqual(prediction[0]["variance"], 1.0 + 1 / 3)
        self.assertEqual(prediction[2]["mean"], 1.0)
        self.assertEqual(prediction[2]["variance"], 2.0)
        metrics = forecast_metrics(case, prediction)
        self.assertEqual(metrics["known"]["pointwise_coverage"], 0.5)
        self.assertEqual(metrics["known"]["unadjusted_pointwise_bands_joint_coverage"], 0.0)
        with self.assertRaises(ValueError):
            forecast_metrics(case, prediction[:-1])


class MonteCarloTests(unittest.TestCase):
    def test_failures_are_counted_and_bias_is_conditional(self):
        result = aggregate(
            [
                {"status": "passed", "parameters": [2.0]},
                {"status": "failed"},
                {"status": "passed", "parameters": [4.0]},
            ],
            [1.0],
        )
        self.assertEqual(result["attempted"], 3)
        self.assertEqual(result["failure_fraction"]["estimate"], 1 / 3)
        self.assertEqual(result["parameters"][0]["bias"]["mean"], 2.0)
        self.assertEqual(result["parameters"][0]["bias"]["mcse"], 1.0)
        self.assertGreater(wilson(0, 10)["wilson95_upper"], 0.0)
        with self.assertRaises(ValueError):
            aggregate([{"status": "source prepared"}], [1.0])
        with self.assertRaises(ValueError):
            wilson(True, 3)

    def test_paired_differences_use_same_replications(self):
        result = paired_summary([1.0, 11.0, 101.0], [0.0, 10.0, 100.0])
        self.assertEqual(result["mean"], 1.0)
        self.assertEqual(result["mcse"], 0.0)
        with self.assertRaises(ValueError):
            paired_summary([1.0], [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
