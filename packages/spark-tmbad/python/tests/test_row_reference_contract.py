"""Validate retained independent constants without importing optional SciPy."""

import hashlib
import json
import math
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"


class RowReferenceContractTests(unittest.TestCase):
    def setUp(self):
        self.reference = json.loads((EXAMPLES / "row_reference_fixtures_v2.json").read_text())

    def test_reference_provenance_binds_the_maintained_generator(self):
        self.assertEqual(self.reference["kind"], "spark-tmbad-independent-row-references")
        self.assertTrue(self.reference["scipy_version"])
        historical = json.loads((EXAMPLES / "row_reference_fixtures.json").read_text())
        self.assertEqual(len(self.reference["cases"]), 35)
        self.assertEqual(self.reference["cases"], historical["cases"])
        self.assertEqual(
            self.reference["generator_sha256"],
            hashlib.sha256((EXAMPLES / "build_row_references.py").read_bytes()).hexdigest(),
        )

    def test_every_row_family_has_finite_shaped_reference_outputs(self):
        self.assertEqual(
            {case["model_id"] for case in self.reference["cases"]},
            {
                "normal",
                "linear_gaussian",
                "quadratic_gaussian",
                "saturating_growth",
                "poisson_exposure",
                "bernoulli_logistic",
                "negative_binomial2",
                "gamma_regression",
            },
        )
        for case in self.reference["cases"]:
            dimension = len(case["theta"])
            self.assertEqual(len(case["expected"]["gradient"]), dimension)
            self.assertTrue(math.isfinite(case["expected"]["loss"]))
            self.assertEqual(len(case["expected"]["hessians"]), 2)
            for hessian in case["expected"]["hessians"]:
                self.assertEqual(len(hessian), dimension * dimension)
                self.assertTrue(all(math.isfinite(value) for value in hessian))

    def test_nb_reference_grid_preserves_shape_and_count_edge_cases(self):
        cases = [
            case for case in self.reference["cases"] if case["model_id"] == "negative_binomial2"
        ]
        self.assertTrue({-4.0, 6.0} <= {case["theta"][2] for case in cases})
        self.assertTrue(
            {0, 64, 65, 1_000_000} <= {row[2] for case in cases for row in case["rows"]}
        )
        self.assertTrue(any(case["tiny_positive_loss"] for case in cases))


if __name__ == "__main__":
    unittest.main()
