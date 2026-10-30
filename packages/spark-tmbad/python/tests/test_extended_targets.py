"""Strict schema2 and named-target controls; no native/Spark execution is claimed."""

import copy
import json
import math
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

from ds60_spark_tmbad import ContractError, FittedModel
from ds60_spark_tmbad._targets import (
    kkt,
    option_object,
    parameter_digest,
    penalties,
    plan_digest,
)
from ds60_spark_tmbad._targets import (
    regularization as canonical_regularization,
)
from extended_fixtures import fitted_document, regularization, runtime


class ExtendedTargetTests(unittest.TestCase):
    def test_independent_digest_vectors_match_jvm_oracles(self):
        payload = json.loads(
            (Path(__file__).parent / "fixtures/named-target-digests.json").read_text()
        )
        for case in payload["cases"]:
            descriptor = {
                "digest": payload["model_digest"],
                "parameter_names": case["names"],
                "parameter_bounds": list(map(list, zip(case["lower"], case["upper"], strict=True))),
            }
            block = {
                "schema_version": 1,
                "coordinate_system": "native_optimizer_parameters",
                "normalization": "summed_likelihood_target",
                "gaussian": case["gaussian"],
                "l1": case["l1"],
            }
            self.assertEqual(
                plan_digest(descriptor, block, case["fixed"]),
                case["expected_target_digest"],
                case["id"],
            )

    def test_map_order_and_negative_zero_do_not_change_identity(self):
        descriptor = runtime().descriptor("normal")
        first = regularization()
        second = {key: first[key] for key in reversed(first)}
        self.assertEqual(
            plan_digest(descriptor, first, {"log_sigma": -0.0}),
            plan_digest(descriptor, second, {"log_sigma": 0.0}),
        )
        self.assertEqual(
            parameter_digest(descriptor, [2.0, -0.0]), parameter_digest(descriptor, [2.0, 0.0])
        )

    def test_prior_names_measures_and_strengths_are_explicit(self):
        descriptor = runtime().descriptor("normal")
        for mutate in (
            lambda block: block.update(coordinate_system="sigma_not_log_sigma"),
            lambda block: block.update(normalization="mean_penalty"),
            lambda block: block["gaussian"]["mu"].update(precision=0),
            lambda block: block["gaussian"]["mu"].update(mean=True),
            lambda block: block["gaussian"].update(unknown={"mean": 0, "precision": 1}),
            lambda block: block["l1"].update(mu=-1),
        ):
            changed = regularization()
            mutate(changed)
            with self.assertRaises(ContractError):
                canonical_regularization(changed, descriptor)
        for options in (
            {"initial_parameters": [0, 0], "regularization": regularization(), "l2_strength": 0.1},
            {
                "initial_parameters": [0, 0],
                "regularization": regularization(),
                "solver": {"method": "bfgs"},
            },
            {"initial_parameters": [0, 0], "solver": {"method": "proximal_gradient"}},
            {"initial_parameters": [0, 21], "fixed_parameters": {"log_sigma": 0}},
        ):
            with self.assertRaises(ContractError):
                option_object(options, descriptor)

    def test_gaussian_scaled_displacement_handles_finite_extreme_target(self):
        descriptor = runtime().descriptor("normal")
        block = regularization(lasso=False)
        block["gaussian"]["mu"] = {"mean": -1e308, "precision": 1e-320}
        q, _, _, gradient, _ = penalties(descriptor, [1e308, 0], block)
        with localcontext() as context:
            context.prec = 80
            delta = Decimal.from_float(1e308) - Decimal.from_float(-1e308)
            expected = Decimal.from_float(1e-320) * delta * delta / 2
        self.assertTrue(math.isclose(q, float(expected), rel_tol=1e-12))
        self.assertTrue(math.isfinite(gradient[0]))
        self.assertGreater(q, 0)

    def test_unbounded_coordinates_are_not_treated_as_fixed(self):
        descriptor = runtime().descriptor("normal")
        self.assertEqual(kkt([0, 0], [-4, 9], [[-1, 1], [0, 0]], descriptor, {"log_sigma": 0}), 3)

    def test_schema2_proximal_fit_accepts_nonzero_smooth_projected_gradient(self):
        selected = runtime()
        document, _ = fitted_document(selected)
        self.assertAlmostEqual(document["fit"]["projected_gradient_inf"], 1, delta=2e-15)
        restored = FittedModel.from_json(
            FittedModel(selected, document).to_json(), runtime=selected
        )
        self.assertTrue(restored.model["fit"]["converged"])
        self.assertEqual(restored.model["target"]["stationarity"]["summed_inf"], 0)

    def test_sum_and_weighted_mean_preserve_the_statistical_target(self):
        selected = runtime()
        summed, _ = fitted_document(selected)
        mean, _ = fitted_document(selected, reduction="weighted_mean")
        FittedModel(selected, summed)
        FittedModel(selected, mean)
        self.assertEqual(
            summed["target"]["target_spec_digest"], mean["target"]["target_spec_digest"]
        )
        self.assertEqual(summed["fit"]["loss"] / 4, mean["fit"]["loss"])
        self.assertEqual(summed["parameters"], mean["parameters"])

    def test_bfgs_and_all_fixed_documents_have_distinct_truthful_status(self):
        selected = runtime()
        for options in ({"proximal": False}, {"all_fixed": True}):
            document, _ = fitted_document(selected, **options)
            FittedModel(selected, document)
        document, _ = fitted_document(selected, all_fixed=True)
        self.assertEqual(document["fit"]["objective_calls"], 1)
        self.assertEqual(document["target"]["free_parameter_count"], 0)
        document["fit"]["status"] = "projected_gradient_tolerance"
        with self.assertRaises(ContractError):
            FittedModel(selected, document)

    def test_target_tampering_and_contradictory_convergence_are_rejected(self):
        selected = runtime()
        original, _ = fitted_document(selected)
        mutations = [
            lambda doc: doc["target"].update(plan_digest="0" * 64),
            lambda doc: doc["target"].update(target_spec_digest="0" * 64),
            lambda doc: doc["target"].update(free_parameter_count=2),
            lambda doc: doc["target"].update(effective_initial_parameters=[0, 0.5]),
            lambda doc: doc["target"].update(
                effective_initial_parameters={"mu": 0, "log_sigma": 0}
            ),
            lambda doc: doc["target"]["loss_components"].update(denominator=2),
            lambda doc: doc["target"]["loss_components"].update(gaussian_quadratic_sum=-1e-12),
            lambda doc: doc["target"]["stationarity"].update(tolerance=1.0001e-6),
            lambda doc: doc["target"]["stationarity"].update(summed_inf=1, reduced_inf=1),
            lambda doc: doc["fit"].update(status="maximum_iterations"),
            lambda doc: doc["fit"].update(active_bounds=[]),
            lambda doc: doc["target"].update(proximal_trace=[]),
            lambda doc: doc["target"]["proximal_trace"][0].update(reduced_kkt_inf=1),
            lambda doc: doc["target"]["solver"].update(max_evaluations=2602),
            lambda doc: doc["fit"].pop("data_ledger"),
        ]
        for mutation in mutations:
            changed = copy.deepcopy(original)
            mutation(changed)
            with self.assertRaises(ContractError):
                FittedModel(selected, changed)

    def test_runtime_version_is_exact_not_an_implicit_migration(self):
        selected = runtime()
        document, _ = fitted_document(selected)
        with self.assertRaises(ContractError):
            FittedModel(runtime("0.1.0"), document)
        document["package_version"] = "0.1.0"
        with self.assertRaises(ContractError):
            FittedModel(selected, document)


if __name__ == "__main__":
    unittest.main()
