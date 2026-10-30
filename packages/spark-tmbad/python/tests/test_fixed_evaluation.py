"""Fixed-point JSON and classic DataFrame bridge contracts, without Spark execution."""

import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from extended_fixtures import evaluation, regularization, runtime

from ds60_spark_tmbad import ContractError, ModelSpec, SparkTMBad, client
from ds60_spark_tmbad._evaluation import validate_evaluation
from ds60_spark_tmbad._json import dumps, loads


class FixedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.runtime = runtime()
        self.options = {"regularization": regularization(), "fixed_parameters": {"log_sigma": 0.0}}
        self.point = [2.5, 0.0]

    def test_full_point_report_preserves_smooth_and_nonsmooth_distinction(self):
        value = evaluation(self.runtime, self.point, self.options)
        result = validate_evaluation(value, self.runtime, "normal", self.point, self.options)
        for observed, expected in zip(result["smooth_gradient_sum"], [-1.0, -21.0], strict=True):
            self.assertAlmostEqual(observed, expected, delta=2e-15)
        self.assertEqual(result["l1_subgradient_sum"], [[1.0, 1.0], [0.0, 0.0]])
        self.assertLessEqual(result["summed_kkt_inf"], 2e-15)
        self.assertNotIn("converged", result)
        zero = evaluation(self.runtime, [0, 0], self.options)
        self.assertEqual(zero["l1_subgradient_sum"][0], [-1.0, 1.0])
        self.assertEqual(zero["summed_kkt_inf"], 15.0)
        validate_evaluation(zero, self.runtime, "normal", [0, 0], self.options)

    def test_weighted_mean_divides_all_new_target_terms_once(self):
        options = self.options | {"reduction": "weighted_mean"}
        summed = evaluation(self.runtime, self.point, self.options)
        mean = evaluation(self.runtime, self.point, options)
        validate_evaluation(mean, self.runtime, "normal", self.point, options)
        for observed, expected in zip(mean["smooth_gradient_reduced"], [-0.25, -5.25], strict=True):
            self.assertAlmostEqual(observed, expected, delta=2e-15)
        self.assertEqual(
            mean["loss_components"]["total_reduced"], summed["loss_components"]["total_reduced"] / 4
        )

    def test_corrupted_identity_counts_and_derivative_parts_are_rejected(self):
        original = evaluation(self.runtime, self.point, self.options)
        mutations = [
            lambda item: item.update(converged=True),
            lambda item: item.update(parameter_digest="0" * 64),
            lambda item: item.update(target_spec_digest="0" * 64),
            lambda item: item.update(parameters=[2.6, 0]),
            lambda item: item.update(parameters={"mu": 2.5, "log_sigma": 0}),
            lambda item: item.update(weight_kind="unit"),
            lambda item: item.update(unit_count=1),
            lambda item: item.update(weight_sum=0),
            lambda item: item.update(partition_count=4097),
            lambda item: item["data_ledger"].update(count=3),
            lambda item: item.update(smooth_gradient_sum=[0, -21]),
            lambda item: item.update(l1_subgradient_sum=[[-1, 1], [0, 0]]),
            lambda item: item.update(summed_kkt_inf=10),
        ]
        for mutate in mutations:
            value = copy.deepcopy(original)
            mutate(value)
            with self.assertRaises(ContractError):
                validate_evaluation(value, self.runtime, "normal", self.point, self.options)

    def test_api_normalizes_named_point_and_rejects_optimizer_options(self):
        calls = []
        response = evaluation(self.runtime, self.point, self.options)

        class Bridge:
            def evaluateShared(self, *args):
                calls.append(args)
                return dumps(response)

        session = SimpleNamespace(_jvm=object(), sparkContext=object())
        frame = SimpleNamespace(_jdf="observations", sparkSession=session, isStreaming=False)
        spec = ModelSpec("normal", {"y": "observation"}, id_columns=["row_id"])
        api = SparkTMBad(self.runtime)
        with patch.object(client, "_bridge", return_value=Bridge()) as lookup:
            result = api.evaluate_shared(
                frame, spec, {"log_sigma": 0, "mu": 2.5}, options=self.options
            )
            lookup.assert_called_once_with(session, required_method="evaluateShared")
            self.assertEqual(loads(calls[0][3]), {"parameters": self.point})
            self.assertNotIn("converged", result)
            for invalid in (
                {"solver": {"method": "bfgs"}},
                {"initial_parameters": [0, 0]},
                {"max_iterations": 20},
            ):
                with self.assertRaises(ContractError):
                    api.evaluate_shared(frame, spec, self.point, options=self.options | invalid)
            with self.assertRaises(ContractError):
                api.evaluate_shared(frame, spec, [2.5, 0.1], options=self.options)
        self.assertEqual(len(calls), 1)

    def test_old_jar_capability_failure_is_explicit_before_submission(self):
        old_class = SimpleNamespace(getMethods=list)
        bridge = SimpleNamespace()
        jvm = SimpleNamespace(
            java=SimpleNamespace(
                lang=SimpleNamespace(
                    Thread=SimpleNamespace(
                        currentThread=lambda: SimpleNamespace(
                            getContextClassLoader=lambda: object()
                        )
                    ),
                    Class=SimpleNamespace(forName=lambda *args: old_class),
                )
            ),
            io=SimpleNamespace(
                ds60=SimpleNamespace(
                    spark=SimpleNamespace(tmbad=SimpleNamespace(PythonBridge=bridge))
                )
            ),
        )
        session = SimpleNamespace(_jvm=jvm, sparkContext=object())
        self.assertIs(client._bridge(session), bridge)
        for method in (
            "evaluateShared",
            "predictAtParameters",
            "predictConditionalAtParameters",
            "forecastAtParameters",
        ):
            with self.assertRaisesRegex(RuntimeError, "loaded.*JAR does not support"):
                client._bridge(session, required_method=method)


if __name__ == "__main__":
    unittest.main()
