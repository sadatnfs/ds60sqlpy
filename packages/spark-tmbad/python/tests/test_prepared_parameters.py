"""Data-only parameter provenance and exact prediction routing without fabricated fits."""

import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from extended_fixtures import runtime

from ds60_spark_tmbad import ContractError, FittedModel, PreparedParameters, PreparedRuntime, client
from ds60_spark_tmbad._json import loads


def declared(selected=None, purpose="simulation_truth", provenance=None):
    selected = runtime() if selected is None else selected
    return PreparedParameters.from_parameters(
        selected,
        "normal",
        parameters={"log_sigma": 0, "mu": 2},
        purpose=purpose,
        parameter_set_id="declared-reference",
        layout={"id_columns": ["row_id"], "group_columns": [], "order_columns": []},
        provenance=provenance
        or {"kind": "simulation_truth", "generator_source_sha256": "e" * 64, "seed": 17},
    )


class ParameterSetTests(unittest.TestCase):
    def test_truth_and_posterior_documents_are_separate_from_fitted_models(self):
        point = declared()
        self.assertEqual(point.document["parameters"], [2.0, 0.0])
        self.assertFalse({"fit", "converged", "trace", "row_count"} & point.document.keys())
        restored = PreparedParameters.from_json(point.to_json(), runtime=point.runtime)
        self.assertEqual(restored.document, point.document)
        with self.assertRaises(ContractError):
            FittedModel.from_json(point.to_json(), runtime=point.runtime)
        posterior = declared(
            purpose="posterior_draw",
            provenance={
                "kind": "posterior_draw",
                "posterior_target_sha256": "1" * 64,
                "sampler_receipt_sha256": "2" * 64,
                "chain_id": "chain-1",
                "draw_index": 0,
            },
        )
        self.assertEqual(posterior.document["purpose"], "posterior_draw")

    def test_provenance_and_wire_shape_refuse_coercions_and_fit_fields(self):
        point = declared()
        mutations = [
            lambda doc: doc.update(fit={"converged": True}),
            lambda doc: doc.update(purpose="posterior_draw"),
            lambda doc: doc["provenance"].update(seed=True),
            lambda doc: doc["provenance"].update(seed=2**53),
            lambda doc: doc["provenance"].update(generator_source_sha256="E" * 64),
            lambda doc: doc["provenance"].update(module="os"),
            lambda doc: doc.update(parameter_set_id="x" * 129),
            lambda doc: doc.update(parameters={"mu": 2, "log_sigma": 0}),
            lambda doc: doc.update(parameters=[2, 21]),
            lambda doc: doc.update(parameter_names=["log_sigma", "mu"]),
            lambda doc: doc.update(package_version="0.1.0"),
            lambda doc: doc["artifact_identity"].update(binary_sha256="0" * 64),
        ]
        for mutation in mutations:
            changed = copy.deepcopy(point.document)
            mutation(changed)
            with self.assertRaises(ContractError):
                PreparedParameters(point.runtime, changed)
        with self.assertRaises(ContractError):
            PreparedParameters.from_parameters(
                point.runtime,
                "normal",
                [2, 0],
                purpose="sensitivity",
                parameter_set_id="point",
                layout=[],
                provenance={"kind": "sensitivity", "reference_sha256": "f" * 64},
            )

    def test_ids_count_unicode_scalars_and_mapping_is_defensively_copied(self):
        selected = runtime()
        parameters = {"mu": 2, "log_sigma": 0}
        layout = {"id_columns": ["row_id"], "group_columns": [], "order_columns": []}
        point = PreparedParameters.from_parameters(
            selected,
            "normal",
            parameters,
            purpose="sensitivity",
            parameter_set_id="\U0001f642" * 128,
            layout=layout,
            provenance={"kind": "sensitivity", "reference_sha256": "f" * 64},
        )
        parameters["mu"] = 999
        layout["id_columns"].append("other")
        self.assertEqual(point.document["parameters"], [2, 0])
        self.assertEqual(point.document["layout"]["id_columns"], ["row_id"])

    def test_group_and_order_layout_requirements_survive_declared_parameters(self):
        manifest = runtime().manifest
        model = manifest["models"][0]
        model["fit_kind"] = "unit"
        model["ordered"] = True
        selected = PreparedRuntime(manifest)
        for layout in (
            {"id_columns": ["id"], "group_columns": [], "order_columns": ["time"]},
            {"id_columns": ["id"], "group_columns": ["group"], "order_columns": []},
            {"id_columns": [], "group_columns": ["group"], "order_columns": ["time"]},
        ):
            with self.assertRaises(ContractError):
                PreparedParameters.from_parameters(
                    selected,
                    "normal",
                    [2, 0],
                    purpose="sensitivity",
                    parameter_set_id="point",
                    layout=layout,
                    provenance={"kind": "sensitivity", "reference_sha256": "f" * 64},
                )

    def test_atomic_local_persistence_keeps_existing_state(self):
        point = declared()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "parameters.json"
            point.save(path)
            before = path.read_bytes()
            self.assertEqual(
                PreparedParameters.load(path, runtime=point.runtime).document, point.document
            )
            with self.assertRaises(FileExistsError):
                point.save(path)
            with self.assertRaises(ContractError):
                point.save(path, overwrite=1)
            self.assertEqual(path.read_bytes(), before)

    def test_prediction_routes_never_send_fitted_model_or_override_fields(self):
        calls = []

        class Bridge:
            def predictAtParameters(self, *args):
                calls.append(("predict", args))
                return "jdf"

            def predictConditionalAtParameters(self, *args):
                calls.append(("conditional", args))
                return "jdf"

            def forecastAtParameters(self, *args):
                calls.append(("forecast", args))
                return "jdf"

        session = SimpleNamespace(_jvm=object(), sparkContext=object())
        future = SimpleNamespace(_jdf="future", sparkSession=session, isStreaming=False)
        history = SimpleNamespace(_jdf="history", sparkSession=session, isStreaming=False)
        point = declared()
        required = []

        def bridge(_, *, required_method=None):
            required.append(required_method)
            return Bridge()

        with (
            patch.object(client, "_bridge", side_effect=bridge),
            patch.object(client, "_wrap", return_value="wrapped"),
        ):
            self.assertEqual(
                point.predict(future, options={"target": "response", "columns": {}}), "wrapped"
            )
            point.predict(
                future,
                history=history,
                options={"target": "response", "columns": {}, "history_columns": {}},
            )
            point.forecast(
                history,
                future,
                options={"target": "response", "future_columns": {}, "history_columns": {}},
            )
            for value in (False, True, "true"):
                with self.assertRaises(ContractError):
                    point.predict(future, options={"allow_unconverged": value})
            other = SimpleNamespace(
                _jdf="other",
                sparkSession=SimpleNamespace(_jvm=object(), sparkContext=object()),
                isStreaming=False,
            )
            with self.assertRaises(ContractError):
                point.forecast(other, future)
        self.assertEqual([name for name, _ in calls], ["predict", "conditional", "forecast"])
        self.assertEqual(
            required[:3],
            ["predictAtParameters", "predictConditionalAtParameters", "forecastAtParameters"],
        )
        for name, arguments in calls:
            document = loads(arguments[1 if name == "predict" else 2])
            self.assertEqual(document["kind"], "spark-tmbad-parameter-set")
            self.assertNotIn("fit", document)


if __name__ == "__main__":
    unittest.main()
