"""Synthetic gallery contracts and independent moments; no Spark runtime claim."""

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))
from gallery.run_gallery import expected_values  # noqa: E402


class GalleryContractTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((EXAMPLES / "gallery/fixtures.json").read_text())["cases"]

    def test_every_model_has_bounded_fit_predict_forecast_and_diagnostics_inputs(self):
        self.assertEqual(len(self.cases), 14)
        for model_id, recipe in self.cases.items():
            with self.subTest(model=model_id):
                self.assertTrue((EXAMPLES / "gallery" / f"{model_id}.py").is_file())
                rows = recipe["training_rows"]
                self.assertTrue(1 <= len(rows) <= 256)
                self.assertEqual(len({row["row_id"] for row in rows}), len(rows))
                self.assertEqual(
                    len(recipe["initial_parameters"]), len(recipe["generating_parameters"])
                )
                self.assertTrue(recipe["prediction_cases"])
                self.assertTrue(recipe["forecast_cases"])
                for row in rows:
                    self.assertTrue(set(recipe["fit_fields"]) <= row.keys())
                for operation in recipe["prediction_cases"] + recipe["forecast_cases"]:
                    self.assertTrue(operation["rows"])
                    for row in operation["rows"]:
                        self.assertNotIn("y", row)
                        self.assertTrue(set(operation["fields"]) <= row.keys())
                    expected = expected_values(model_id, recipe["generating_parameters"], operation)
                    self.assertEqual(len(expected), len(operation["rows"]))
                    self.assertTrue(all(math.isfinite(value) for row in expected for value in row))

    def test_new_group_cases_exercise_future_only_keys(self):
        for recipe in self.cases.values():
            if not recipe["group_columns"]:
                continue
            groups = {row["series"] for row in recipe["training_rows"]}
            new = next(
                operation for operation in recipe["forecast_cases"] if not operation["history_rows"]
            )
            self.assertTrue(all(row["series"] not in groups for row in new["rows"]))

    def test_gaussian_exact_and_laplace_gallery_use_identical_observations(self):
        exact = self.cases["gaussian_random_intercept"]
        approximate = self.cases["gaussian_random_intercept_laplace"]
        self.assertEqual(exact["training_rows"], approximate["training_rows"])
        self.assertEqual(exact["forecast_cases"], approximate["forecast_cases"])

    def test_checked_in_fixtures_match_the_deterministic_generator(self):
        subprocess.run(
            [sys.executable, str(EXAMPLES / "gallery/build_fixtures.py"), "--check"], check=True
        )

    def test_logistic_extreme_tail_retains_positive_variance(self):
        operation = {"rows": [{"row_id": 1, "x": 0.0}], "history_rows": []}
        value = expected_values("bernoulli_logistic", [40.0, 0.0], operation)[0]
        self.assertEqual(value[0], 1.0)
        self.assertGreater(value[1], 0.0)
        self.assertTrue(math.isclose(value[1], math.exp(-40.0), rel_tol=1e-14))


if __name__ == "__main__":
    unittest.main()
