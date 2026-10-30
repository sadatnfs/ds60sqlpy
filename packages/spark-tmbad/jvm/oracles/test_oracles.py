"""Independent mathematical fixture checks, never a Scala execution claim."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from fractions import Fraction as F
from pathlib import Path

SCRIPT = Path(__file__).with_name("build_oracles.py")
SPEC = importlib.util.spec_from_file_location("target_oracles", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
oracles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oracles)


class MathematicalOracles(unittest.TestCase):
    def setUp(self):
        self.cases = {case["id"]: case for case in oracles.cases()}

    def test_exact_orthogonal_soft_threshold_and_unpenalized_intercept(self):
        result = self.cases["orthogonal_lasso"]["expected"]
        self.assertEqual(result["rational_parameters"], ["2", "7/10", "0"])

    def test_correlated_nonzero_center_and_l1_zero_have_exact_solution(self):
        result = self.cases["correlated_prior_l1"]["expected"]
        self.assertEqual(result["rational_parameters"], ["179/95", "44/95", "0"])

    def test_fixed_nuisance_is_conditioned_during_the_solve(self):
        case = self.cases["fixed_nuisance"]
        self.assertEqual(case["expected"]["rational_parameters"], ["281/235", "-21/235", "4/5"])
        without = copy.deepcopy(case)
        without["fixed"] = {}
        unconstrained = oracles.active_set_reference(without)
        self.assertNotEqual(
            unconstrained["rational_parameters"][:2], case["expected"]["rational_parameters"][:2]
        )

    def test_box_normal_cones_and_all_fixed_coordinates(self):
        self.assertEqual(self.cases["positive_box_excludes_zero"]["expected"]["parameters"], [1.0])
        self.assertEqual(self.cases["negative_upper_box"]["expected"]["parameters"], [-1.0])
        self.assertEqual(self.cases["all_fixed"]["expected"]["free_parameter_count"], 0)
        self.assertEqual(oracles.kkt([F(2)], [F(999)], [F(3)], [F(2)], [F(2)]), [F(0)])

    def test_weighted_mean_scales_every_target_component(self):
        case = self.cases["correlated_prior_l1"]
        expected = case["expected"]
        self.assertAlmostEqual(
            expected["composite_weighted_mean"] * case["weight"], expected["composite_sum"]
        )
        wrong = copy.deepcopy(case)
        for term in wrong["gaussian"].values():
            term["precision"] *= case["weight"]
        wrong["l1"] = {name: value * case["weight"] for name, value in wrong["l1"].items()}
        self.assertNotEqual(
            oracles.active_set_reference(wrong)["parameters"], expected["parameters"]
        )

    def test_zero_subgradient_and_exact_threshold(self):
        self.assertEqual(self.cases["exact_threshold_zero"]["expected"]["parameters"], [0.0])
        self.assertEqual(oracles.kkt([F(0)], [F(-1)], [F(1)], [None], [None]), [F(0)])
        self.assertEqual(oracles.kkt([F(0)], [F(-2)], [F(1)], [None], [None]), [F(1)])

    def test_oracle_rejects_nonconvex_matrix_instead_of_certifying_kkt_only(self):
        with self.assertRaisesRegex(ValueError, "positive definite"):
            oracles.assert_positive_definite(oracles.matrix([[1, 2], [2, 1]]))

    def test_digest_is_term_order_independent_but_binds_prior_center_and_fixed_value(self):
        case = copy.deepcopy(self.cases["fixed_nuisance"])
        case["gaussian"]["intercept"] = {"mean": 0.4, "precision": 2.5}
        expected = oracles.target_digest(case)
        case["gaussian"] = dict(reversed(list(case["gaussian"].items())))
        self.assertEqual(oracles.target_digest(case), expected)
        case["gaussian"]["intercept"]["mean"] = 0.5
        self.assertNotEqual(oracles.target_digest(case), expected)
        case["gaussian"]["intercept"]["mean"] = 0.4
        case["fixed"]["nuisance"] = 0.9
        self.assertNotEqual(oracles.target_digest(case), expected)


if __name__ == "__main__":
    unittest.main()
