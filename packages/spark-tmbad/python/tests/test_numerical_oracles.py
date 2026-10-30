"""Validate independent reference mathematics. This does not execute native AD."""

import importlib.util
import math
import unittest
from pathlib import Path

path = Path(__file__).parents[1] / "examples" / "numerical_oracles.py"
spec = importlib.util.spec_from_file_location("independent_numerical_oracles", path)
oracles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracles)


class NumericalOracleTests(unittest.TestCase):
    def assert_close(self, actual, expected, tolerance=3e-6):
        self.assertTrue(
            math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)
        )

    def test_gaussian_exact_gradient_at_changed_data_and_parameters(self):
        for observations in ([1.2, -0.4, 2.8], [-3.0, -2.7, -1.5, -2.0]):
            for theta in ([0.3, -0.5, 0.2], [-1.0, 0.4, -0.7]):
                reference = oracles.gaussian_random_intercept(theta, observations)
                for step in (2e-5, 5e-6):
                    numerical = oracles.finite_difference_gradient(
                        lambda point, observations=observations: oracles.gaussian_random_intercept(
                            point, observations
                        )["loss"],
                        theta,
                        step,
                    )
                    for actual, expected in zip(reference["gradient"], numerical, strict=True):
                        self.assert_close(actual, expected)

    def test_gaussian_existing_group_and_new_group_are_different(self):
        theta = [2.0, math.log(0.5), math.log(1.2)]
        history = [4.0, 3.8, 4.2]
        conditional = oracles.gaussian_random_intercept_prediction(theta, history)
        prior = oracles.gaussian_random_intercept_prediction(theta)
        self.assertGreater(conditional[0], prior[0])
        self.assertLess(conditional[1], prior[1])
        self.assert_close(prior[1], 0.25 + 1.44)
        self.assert_close(conditional[1], 0.25 + 1 / (1 / 1.44 + 3 / 0.25))

    def test_poisson_laplace_outer_gradient_includes_mode_curvature_path(self):
        for rows in ([[0.5, 0], [1.5, 2], [2.0, 5]], [[1.0, 0], [0.8, 0]], [[0.4, 8], [3.0, 11]]):
            for theta in ([-0.4, -0.3], [0.7, 0.2], [1.0, -1.0]):
                reference = oracles.poisson_random_intercept(theta, rows)
                self.assertLess(abs(reference["score"]), 1e-9)
                self.assertGreater(reference["curvature"], 0)
                for step in (2e-5, 5e-6):
                    numerical = oracles.finite_difference_gradient(
                        lambda point, rows=rows: oracles.poisson_random_intercept(point, rows)[
                            "loss"
                        ],
                        theta,
                        step,
                    )
                    for actual, expected in zip(reference["gradient"], numerical, strict=True):
                        self.assert_close(actual, expected)
        reference = oracles.poisson_random_intercept([-0.4, -0.3], [[0.5, 0], [1.5, 2], [2.0, 5]])
        # Frozen-mode joint differentiation misses the log-curvature derivative.
        latent = reference["mode"]
        frozen_beta = 4.0 * math.exp(-0.4 + latent) - 7
        self.assertGreater(abs(reference["gradient"][0] - frozen_beta), 0.01)

    def test_laplace_value_is_not_claimed_to_equal_the_exact_poisson_integral(self):
        theta, rows = [0.1, 0.0], [[0.5, 0], [1.5, 2], [2.0, 5]]
        reference = oracles.poisson_random_intercept(theta, rows)
        # Independent composite Simpson integration, centered by the joint mode.
        shift = oracles.poisson_joint(theta, rows, reference["mode"])
        count, lower, upper = 10000, -12.0, 12.0
        step = (upper - lower) / count
        values = [
            math.exp(shift - oracles.poisson_joint(theta, rows, lower + index * step))
            for index in range(count + 1)
        ]
        integral = (
            step
            / 3
            * (
                values[0]
                + values[-1]
                + 4 * math.fsum(values[1:-1:2])
                + 2 * math.fsum(values[2:-1:2])
            )
        )
        exact_loss = shift - math.log(integral)
        self.assertGreater(abs(reference["loss"] - exact_loss), 1e-4)
        self.assertLess(abs(reference["loss"] - exact_loss), 0.1)

    def test_poisson_existing_group_moments_use_the_approximate_posterior(self):
        theta, history = [0.2, -0.1], [[1.0, 4], [2.0, 9]]
        existing = oracles.poisson_random_intercept_prediction(theta, 1.5, history)
        new = oracles.poisson_random_intercept_prediction(theta, 1.5)
        self.assertGreater(existing[0], new[0])
        self.assertGreater(existing[1], existing[0])
        self.assertGreater(new[1], new[0])

    def test_ar1_mean_and_variance_propagate_each_innovation(self):
        theta = [2.0, math.atanh(-0.5), math.log(0.7)]
        result = oracles.ar1_forecast(theta, [1, 2, 3], last_observation=4.0)
        for actual, expected in zip(
            result, [[1.0, 0.49], [2.5, 0.6125], [1.75, 0.643125]], strict=True
        ):
            self.assert_close(actual[0], expected[0])
            self.assert_close(actual[1], expected[1])
        stationary = oracles.ar1_forecast(theta, [1, 2, 3])
        for row in stationary:
            self.assert_close(row[0], 2.0)
            self.assert_close(row[1], 0.49 / 0.75)
        self.assertNotEqual(result[0], stationary[0])

    def test_combined_dense_covariance_gradient_has_independent_finite_difference_check(self):
        rows = [[0, 0.7], [1, -0.2], [2, 1.4], [3, 0.3]]
        for theta in ([0.2, math.atanh(0.6), -0.4, -0.1], [-0.3, math.atanh(-0.4), 0.1, -0.7]):
            reference = oracles.gaussian_ar1_random_intercept(theta, rows)
            for step in (2e-5, 5e-6):
                numerical = oracles.finite_difference_gradient(
                    lambda point: oracles.gaussian_ar1_random_intercept(point, rows)["loss"],
                    theta,
                    step,
                )
                for actual, expected in zip(reference["gradient"], numerical, strict=True):
                    self.assert_close(actual, expected)

    def test_combined_model_reduces_to_random_intercept_at_zero_phi(self):
        theta = [0.2, 0.0, -0.4, -0.1]
        rows = [[0, 0.7], [1, -0.2], [2, 1.4], [3, 0.3]]
        combined = oracles.gaussian_ar1_random_intercept(theta, rows)
        simple = oracles.gaussian_random_intercept(
            [theta[0], theta[2], theta[3]], [row[1] for row in rows]
        )
        self.assert_close(combined["loss"], simple["loss"])
        for actual, expected in zip(
            [combined["gradient"][index] for index in (0, 2, 3)], simple["gradient"], strict=True
        ):
            self.assert_close(actual, expected)
        predicted = oracles.gaussian_ar1_random_intercept_prediction(theta, [4, 5, 6], rows)
        expected = oracles.gaussian_random_intercept_prediction(
            [theta[0], theta[2], theta[3]], [row[1] for row in rows]
        )
        for row in predicted:
            for actual, reference in zip(row, expected, strict=True):
                self.assert_close(actual, reference)

    def test_combined_conditional_variance_is_smaller_than_new_series_variance(self):
        theta = [0.2, math.atanh(-0.4), -0.4, -0.1]
        rows = [[0, 0.7], [1, -0.2], [2, 1.4], [3, 0.3]]
        conditional = oracles.gaussian_ar1_random_intercept_prediction(theta, [4, 5, 6], rows)
        prior = oracles.gaussian_ar1_random_intercept_prediction(theta, [4, 5, 6])
        for observed, new in zip(conditional, prior, strict=True):
            self.assertGreater(observed[1], 0)
            self.assertLess(observed[1], new[1])
        self.assertNotEqual(conditional[0][0], prior[0][0])

    def test_two_dimensional_poisson_laplace_gradient_and_full_covariance(self):
        rows = [[-1.0, 1.0, 0], [0.0, 2.0, 3], [0.7, 0.5, 2], [1.0, 1.5, 5]]
        for theta in ([0.2, -0.3, -0.4, -0.7], [-0.5, 0.6, 0.1, -0.2]):
            reference = oracles.poisson_random_slope(theta, rows)
            self.assertLess(max(map(abs, reference["score"])), 1e-9)
            self.assertNotEqual(reference["latent_covariance"][0][1], 0.0)
            for step in (2e-5, 5e-6):
                numerical = oracles.finite_difference_gradient(
                    lambda point: oracles.poisson_random_slope(point, rows)["loss"], theta, step
                )
                for actual, expected in zip(reference["gradient"], numerical, strict=True):
                    self.assert_close(actual, expected)
            for x in (-0.8, 0.5):
                existing = oracles.poisson_random_slope_prediction(theta, x, 1.2, rows)
                prior = oracles.poisson_random_slope_prediction(theta, x, 1.2)
                self.assertGreater(existing[1], existing[0])
                self.assertGreater(prior[1], prior[0])
                self.assertNotEqual(existing, prior)


if __name__ == "__main__":
    unittest.main()
