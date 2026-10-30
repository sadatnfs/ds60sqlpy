"""Pure Python contracts only; real Spark acceptance lives in examples/."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ds60_spark_tmbad import ContractError, FittedModel, ModelSpec, PreparedRuntime, SparkTMBad
from ds60_spark_tmbad._json import MAX_JSON_BYTES, dumps, read
from ds60_spark_tmbad.persistence import save_model


def manifest():
    return {
        "schema_version": 1,
        "kind": "spark-tmbad-artifact",
        "package_version": "0.1.0",
        "protocol": 1,
        "build_id": "a" * 64,
        "platform": {"os": "linux", "arch": "arm64"},
        "binary": {"path": "/prepared/tmbad-worker", "sha256": "b" * 64},
        "engine": {"name": "TMBad", "version": "1.9.25", "source_sha256": "c" * 64},
        "models": [
            {
                "id": "normal",
                "version": "1",
                "digest": "d" * 64,
                "fit_kind": "rows",
                "fit_fields": ["y"],
                "parameter_names": ["mu", "log_sigma"],
                "parameter_bounds": [[None, None], [-20, 20]],
                "marginalization": "none",
                "random_dimension": 0,
                "max_unit_rows": 256,
                "derivative_orders": [1, 2],
                "ordered": False,
                "predict": {
                    "response": {
                        "fields": [],
                        "columns": ["mean", "sd"],
                        "needs_history": False,
                        "conditioning": "fitted parameters",
                        "uncertainty": "observation only",
                    }
                },
                "forecast": {},
            }
        ],
    }


def model(runtime):
    return {
        "schema_version": 1,
        "kind": "spark-tmbad-model",
        "package_version": "0.1.0",
        "model_id": "normal",
        "model_digest": "d" * 64,
        "artifact_identity": runtime.identity("normal"),
        "parameters": [2.0, 0.5],
        "parameter_names": ["mu", "log_sigma"],
        "spec": ModelSpec("normal", {"y": "observation"}, id_columns=["row_id"]).to_dict(),
        "fit": {
            "converged": True,
            "status": "converged",
            "reason": "projected gradient",
            "iterations": 0,
            "objective_calls": 1,
            "loss": 5.0,
            "raw_gradient_inf": 0.0,
            "projected_gradient_inf": 0.0,
            "active_bounds": [],
            "row_count": 4,
            "unit_count": 0,
            "weight_sum": 4.0,
            "trace": [],
        },
    }


class RuntimeContractTests(unittest.TestCase):
    def test_import_never_initializes_spark_or_numerical_backends(self):
        code = """import sys
import ds60_spark_tmbad
for forbidden in ('pyspark', 'numpy', 'scipy', 'torch', 'rpy2'):
    assert forbidden not in sys.modules, forbidden
assert ds60_spark_tmbad.__version__ == '0.1.0'
"""
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / "src"))
        subprocess.run([sys.executable, "-c", code], env=env, check=True)

    def test_runtime_is_defensively_copied_and_paths_are_relocatable(self):
        original = manifest()
        runtime = PreparedRuntime(original)
        original["models"][0]["digest"] = "0" * 64
        self.assertEqual(runtime.descriptor("normal")["digest"], "d" * 64)
        moved = runtime.manifest
        moved["binary"]["path"] = "/other/tmbad-worker"
        self.assertEqual(runtime.identity("normal"), PreparedRuntime(moved).identity("normal"))
        self.assertEqual(runtime.model_ids, ("normal",))

    def test_local_file_hash_verification_is_explicit_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "worker"
            binary.write_bytes(b"a prepared artifact, not executed")
            value = manifest()
            value["binary"] = {
                "path": str(binary),
                "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            }
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            runtime = PreparedRuntime.from_manifest(path)
            binary.write_bytes(b"changed")
            with self.assertRaisesRegex(ContractError, "SHA-256"):
                runtime.verify_files()

    def test_wrong_protocol_or_nonabsolute_binary_is_rejected(self):
        for key, value in (
            ("protocol", 2),
            ("protocol", True),
            ("build_id", "bad"),
            ("platform", {"os": "darwin", "arch": "arm64"}),
        ):
            changed = manifest()
            changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ContractError):
                PreparedRuntime(changed)
        changed = manifest()
        changed["binary"]["path"] = "worker"
        with self.assertRaises(ContractError):
            PreparedRuntime(changed)

    def test_unknown_and_duplicate_models_are_rejected(self):
        runtime = PreparedRuntime(manifest())
        with self.assertRaisesRegex(ContractError, "absent"):
            runtime.descriptor("unprepared")
        changed = manifest()
        changed["models"].append(copy.deepcopy(changed["models"][0]))
        with self.assertRaisesRegex(ContractError, "Duplicate"):
            PreparedRuntime(changed)

    def test_descriptor_requires_the_complete_shared_protocol(self):
        for field in ("marginalization", "random_dimension", "max_unit_rows", "derivative_orders"):
            changed = manifest()
            del changed["models"][0][field]
            with self.subTest(field=field), self.assertRaisesRegex(ContractError, "descriptor"):
                PreparedRuntime(changed)
        for field, value in (
            ("random_dimension", True),
            ("max_unit_rows", 257),
            ("derivative_orders", [True]),
            ("derivative_orders", [1, {}]),
            ("marginalization", "arbitrary"),
        ):
            changed = manifest()
            changed["models"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ContractError):
                PreparedRuntime(changed)


class SpecContractTests(unittest.TestCase):
    def test_exact_fields_and_complete_groups_are_required(self):
        descriptor = PreparedRuntime(manifest()).descriptor("normal")
        with self.assertRaisesRegex(ContractError, "fit_fields"):
            ModelSpec("normal", {"wrong": "value"}, id_columns=["id"]).validate_descriptor(
                descriptor
            )
        descriptor["fit_kind"] = "unit"
        with self.assertRaisesRegex(ContractError, "group_columns"):
            ModelSpec("normal", {"y": "value"}, id_columns=["id"]).validate_descriptor(descriptor)
        descriptor["ordered"] = True
        with self.assertRaisesRegex(ContractError, "order_columns"):
            ModelSpec(
                "normal", {"y": "value"}, id_columns=["id"], group_columns=["series"]
            ).validate_descriptor(descriptor)
        ModelSpec(
            "normal",
            {"y": "value"},
            id_columns=["id"],
            group_columns=["series"],
            order_columns=["time"],
        ).validate_descriptor(descriptor)

    def test_identity_keys_and_unknown_spec_fields_are_rejected(self):
        for ids in ([], ["id", "id"], "id"):
            with self.subTest(ids=ids), self.assertRaises(ContractError):
                ModelSpec("normal", {"y": "value"}, id_columns=ids)
        value = ModelSpec("normal", {"y": "value"}, id_columns=["id"]).to_dict()
        value["command"] = "not allowed"
        with self.assertRaisesRegex(ContractError, "Unknown"):
            ModelSpec.from_dict(value)

    def test_invalid_dataframes_fail_before_jvm_execution(self):
        api = SparkTMBad(PreparedRuntime(manifest()))
        with self.assertRaisesRegex(ContractError, "classic PySpark DataFrame"):
            api.fit_shared([], ModelSpec("normal", {"y": "value"}, id_columns=["id"]))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.runtime = PreparedRuntime(manifest())
        self.value = model(self.runtime)

    def test_json_round_trip_and_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fit.json"
            fitted = FittedModel(self.runtime, self.value)
            fitted.save(path)
            loaded = FittedModel.load(path, runtime=self.runtime)
            self.assertEqual(loaded.model, fitted.model)
            with self.assertRaises(FileExistsError):
                fitted.save(path)
            changed = self.value.copy()
            changed["parameters"] = [3.0, 0.5]
            FittedModel(self.runtime, changed).save(path, overwrite=True)
            self.assertEqual(
                FittedModel.load(path, runtime=self.runtime).model["parameters"][0], 3.0
            )

    def test_common_wire_json_is_strict_and_source_bound(self):
        fitted = FittedModel(self.runtime, self.value)
        self.assertEqual(
            FittedModel.from_json(fitted.to_json(), runtime=self.runtime).model, self.value
        )
        with self.assertRaisesRegex(ContractError, "Duplicate"):
            FittedModel.from_json('{"kind":"a","kind":"b"}', runtime=self.runtime)

    def test_maximum_size_json_remains_loadable_after_save(self):
        value = {"records": ["x" * 1_000_000] * 4 + [""]}
        value["records"][-1] = "x" * (MAX_JSON_BYTES - len(dumps(value).encode("utf-8")))
        raw = dumps(value)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "maximum.json"
            save_model(path, raw, overwrite=False)
            self.assertEqual(path.stat().st_size, MAX_JSON_BYTES)
            self.assertEqual(read(path), value)

    def test_source_binary_and_parameter_changes_are_rejected(self):
        changes = [
            ("model_digest", "e" * 64),
            ("parameters", [1]),
            ("parameters", [True, 1]),
            ("parameters", [1, 21]),
            ("parameter_names", ["log_sigma", "mu"]),
            ("artifact_identity", {**self.value["artifact_identity"], "binary_sha256": "f" * 64}),
        ]
        for key, value in changes:
            changed = copy.deepcopy(self.value)
            changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ContractError):
                FittedModel(self.runtime, changed)

    def test_saved_model_cannot_silently_change_architecture_or_jar(self):
        other = self.runtime.manifest
        other["platform"]["arch"] = "amd64"
        with self.assertRaisesRegex(ContractError, "artifact identity"):
            FittedModel(PreparedRuntime(other), self.value)
        with_jar = self.runtime.manifest
        with_jar["jvm"] = {
            "path": "/prepared/spark-tmbad.jar",
            "sha256": "e" * 64,
            "spark_version": "4.0.1",
            "scala_binary_version": "2.13",
            "java_min": 17,
        }
        runtime = PreparedRuntime(with_jar)
        value = model(runtime)
        with_jar["jvm"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ContractError, "artifact identity"):
            FittedModel(PreparedRuntime(with_jar), value)

    def test_code_loader_fields_and_remote_paths_are_rejected(self):
        changed = copy.deepcopy(self.value)
        changed["python_module"] = "os"
        with self.assertRaises(ContractError):
            FittedModel(self.runtime, changed)
        fitted = FittedModel(self.runtime, self.value)
        with self.assertRaisesRegex(ContractError, "local filesystem"):
            fitted.save("s3://bucket/model.json")

    def test_failed_fit_prediction_needs_an_explicit_diagnostic_override(self):
        failed = copy.deepcopy(self.value)
        failed["fit"]["converged"] = False
        failed["fit"]["status"] = "stalled"
        fitted = FittedModel(self.runtime, failed)
        with self.assertRaisesRegex(ContractError, "converged fit"):
            fitted.predict(object())
        with self.assertRaisesRegex(ContractError, "converged fit"):
            fitted.forecast(object(), object())
        with self.assertRaisesRegex(ContractError, "explicit boolean"):
            fitted.predict(object(), options={"allow_unconverged": "true"})
        # The explicit diagnostic override reaches DataFrame validation, without
        # pretending this pure test executed a real Spark prediction.
        with self.assertRaisesRegex(ContractError, "classic PySpark DataFrame"):
            fitted.predict(object(), options={"allow_unconverged": True})
        self.assertFalse(fitted.model["fit"]["converged"])
        self.assertEqual(fitted.model["fit"]["status"], "stalled")

    def test_malformed_diagnostics_and_incomplete_saved_specs_are_rejected(self):
        for field, value in (
            ("loss", "not numeric"),
            ("row_count", -1),
            ("weight_sum", 0),
            ("objective_calls", True),
            ("active_bounds", [2]),
            ("trace", ["invalid"]),
            ("projected_gradient_inf", -1.0),
        ):
            changed = copy.deepcopy(self.value)
            changed["fit"][field] = value
            with self.subTest(field=field), self.assertRaises(ContractError):
                FittedModel(self.runtime, changed)
        changed = copy.deepcopy(self.value)
        changed["fit"] = {"converged": True}
        with self.assertRaises(ContractError):
            FittedModel(self.runtime, changed)
        for field in ("group_columns", "order_columns", "weight_column"):
            changed = copy.deepcopy(self.value)
            del changed["spec"][field]
            with self.subTest(field=field), self.assertRaisesRegex(ContractError, "fitted spec"):
                FittedModel(self.runtime, changed)

    def test_nonboolean_overwrite_never_replaces_existing_file(self):
        fitted = FittedModel(self.runtime, self.value)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.json"
            path.write_text("preserve exactly", encoding="utf-8")
            for flag in ("false", "true", 0, 1, None):
                with (
                    self.subTest(flag=flag),
                    self.assertRaisesRegex(ContractError, "explicit boolean"),
                ):
                    fitted.save(path, overwrite=flag)
                self.assertEqual(path.read_text(), "preserve exactly")
                self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_fit_counts_match_factorization_and_ledger(self):
        changed = copy.deepcopy(self.value)
        changed["fit"]["unit_count"] = 1
        with self.assertRaisesRegex(ContractError, "factorization"):
            FittedModel(self.runtime, changed)

        changed = copy.deepcopy(self.value)
        changed["fit"]["data_ledger"] = {"count": 3, "xor": "0", "sum": "0"}
        with self.assertRaisesRegex(ContractError, "ledger count"):
            FittedModel(self.runtime, changed)

    def test_reviewed_candidate_rejections_are_bounded_diagnostics(self):
        changed = copy.deepcopy(self.value)
        changed["fit"]["rejected_candidates"] = 1
        self.assertEqual(FittedModel(self.runtime, changed).model["fit"]["rejected_candidates"], 1)
        for count in (-1, 2, True, 0.5):
            changed["fit"]["rejected_candidates"] = count
            with (
                self.subTest(count=count),
                self.assertRaisesRegex(ContractError, "rejected candidate"),
            ):
                FittedModel(self.runtime, changed)


if __name__ == "__main__":
    unittest.main()
