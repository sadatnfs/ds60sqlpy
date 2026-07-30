"""Tests for python-stats-01."""

from __future__ import annotations

import unittest
from typing import ClassVar

from python.professional.solutions.py_stats_01_resampling_experiments_solution import (
    ExperimentPlan,
    Observation,
    bootstrap_difference_interval,
    claim_scope,
    difference_in_means,
    holm_adjust,
    load_observations,
    minimum_sample_per_arm,
    per_look_alpha,
    permutation_test,
    split_outcomes,
    standardized_balance_difference,
    standardized_mean_difference,
)


class ResamplingExperimentTests(unittest.TestCase):
    observations: ClassVar[list[Observation]]
    control: ClassVar[list[float]]
    treatment: ClassVar[list[float]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.observations = load_observations()
        cls.control, cls.treatment = split_outcomes(cls.observations)

    def test_fixture_is_balanced_and_effect_is_visible(self) -> None:
        self.assertEqual(len(self.control), 8)
        self.assertEqual(len(self.treatment), 8)
        self.assertEqual(difference_in_means(self.control, self.treatment), 2.0)
        self.assertGreater(standardized_mean_difference(self.control, self.treatment), 1)

        control_pre = [row.pre_score for row in self.observations if row.variant == "control"]
        treatment_pre = [row.pre_score for row in self.observations if row.variant == "treatment"]
        self.assertEqual(
            standardized_balance_difference(control_pre, treatment_pre),
            0.0,
        )

    def test_bootstrap_is_seeded_and_excludes_zero(self) -> None:
        first = bootstrap_difference_interval(
            self.control,
            self.treatment,
            resamples=1_000,
            seed=7,
        )
        second = bootstrap_difference_interval(
            self.control,
            self.treatment,
            resamples=1_000,
            seed=7,
        )
        self.assertEqual(first, second)
        self.assertLess(0, first.lower)
        self.assertLess(first.lower, first.estimate)
        self.assertLess(first.estimate, first.upper)

    def test_exact_permutation_test_counts_assignments(self) -> None:
        result = permutation_test(self.control, self.treatment)
        self.assertTrue(result.exact)
        self.assertEqual(result.permutations, 12_870)
        self.assertLess(result.p_value, 0.05)

    def test_power_and_multiple_comparison_plans(self) -> None:
        self.assertEqual(minimum_sample_per_arm(0.5), 63)
        adjusted = holm_adjust([0.01, 0.04, 0.03])
        self.assertEqual(adjusted, [0.03, 0.06, 0.06])
        self.assertAlmostEqual(per_look_alpha(0.05, 5), 0.01)
        plan = ExperimentPlan("account", "conversion_7d", 63)
        self.assertEqual(plan.primary_metric, "conversion_7d")

    def test_claim_boundary_requires_design_protections(self) -> None:
        self.assertEqual(
            claim_scope(
                randomized=True,
                allocation_intact=True,
                severe_attrition=False,
            ),
            "causal",
        )
        self.assertEqual(
            claim_scope(
                randomized=False,
                allocation_intact=True,
                severe_attrition=False,
            ),
            "associational",
        )
        self.assertEqual(
            claim_scope(
                randomized=True,
                allocation_intact=True,
                severe_attrition=True,
            ),
            "associational",
        )


if __name__ == "__main__":
    unittest.main()
