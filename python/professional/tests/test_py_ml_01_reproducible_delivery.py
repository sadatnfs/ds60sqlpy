"""Tests for python-ml-01."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from python.professional.solutions.py_ml_01_reproducible_delivery_solution import (
    FeatureSchema,
    FeatureSpec,
    LocalRegistry,
    PromotionEvidence,
    Record,
    RuntimeRequirement,
    canonical_json,
    canonical_record_hash,
    compatibility_report,
    fit_linear_model,
    manifest_payload,
    sha256_text,
    verify_bundle,
    write_bundle,
)


class ReproducibleDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = FeatureSchema(1, (FeatureSpec("x", "float"),))
        self.runtime = RuntimeRequirement((3, 11), (3, 13), (("runtime", "1"),))
        self.records: list[Record] = [
            {"record_id": "r1", "x": 0.0, "y": 1.0},
            {"record_id": "r2", "x": 1.0, "y": 3.0},
            {"record_id": "r3", "x": 2.0, "y": 5.0},
        ]

    def test_snapshot_hash_is_order_independent_but_content_sensitive(self) -> None:
        forward = canonical_record_hash(self.records)
        reverse = canonical_record_hash(list(reversed(self.records)))
        changed = canonical_record_hash(
            [*self.records[:-1], {"record_id": "r3", "x": 2.0, "y": 6.0}]
        )
        self.assertEqual(forward, reverse)
        self.assertNotEqual(forward, changed)
        with self.assertRaises(ValueError):
            canonical_record_hash([self.records[0], self.records[0]])

    def test_model_and_verified_bundle_are_deterministic(self) -> None:
        model = fit_linear_model([(0, 1), (1, 3), (2, 5)])
        self.assertAlmostEqual(model.predict({"x": 3}), 7.0)
        with tempfile.TemporaryDirectory(prefix="ds60-model-test-") as directory:
            bundle = Path(directory) / "bundle"
            manifest = write_bundle(
                bundle,
                model=model,
                schema=self.schema,
                data_snapshot_sha256=canonical_record_hash(self.records),
                runtime=self.runtime,
            )
            verify_bundle(bundle, manifest)
            digest = sha256_text(canonical_json(manifest_payload(manifest)))
            self.assertEqual(len(digest), 64)

            (bundle / "model.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "artifact hash"):
                verify_bundle(bundle, manifest)

    def test_compatibility_reports_all_reasons(self) -> None:
        good = compatibility_report(
            expected_schema=self.schema,
            actual_schema=self.schema,
            runtime=self.runtime,
            python_version=(3, 11),
            package_versions={"runtime": "1.5"},
        )
        self.assertTrue(good.compatible)

        incompatible = compatibility_report(
            expected_schema=self.schema,
            actual_schema=FeatureSchema(2, (FeatureSpec("other", "float"),)),
            runtime=self.runtime,
            python_version=(3, 13),
            package_versions={"runtime": "2.0"},
        )
        self.assertFalse(incompatible.compatible)
        self.assertEqual(len(incompatible.reasons), 3)

    def test_registry_requires_evidence_and_records_rollback(self) -> None:
        approved_v1 = PromotionEvidence(True, True, "accuracy", 0.90, 0.85, "a" * 64)
        approved_v2 = PromotionEvidence(True, True, "accuracy", 0.92, 0.85, "b" * 64)
        registry = LocalRegistry()
        registry.register("1", approved_v1)
        registry.stage("1")
        registry.promote("1", reason="local compatibility suite passed")
        registry.register("2", approved_v2)
        registry.stage("2")
        registry.promote("2", reason="reviewed metric improvement")
        production = registry.production()
        self.assertIsNotNone(production)
        assert production is not None
        self.assertEqual(production.version, "2")

        registry.rollback("1", reason="incident drill: latency regression")
        production = registry.production()
        self.assertIsNotNone(production)
        assert production is not None
        self.assertEqual(production.version, "1")
        self.assertEqual(registry.events[-1].action, "rollback")
        self.assertIn("latency", registry.events[-1].reason)

        rejected = PromotionEvidence(False, True, "accuracy", 0.99, 0.85, "c" * 64)
        registry.register("3", rejected)
        with self.assertRaisesRegex(ValueError, "evidence"):
            registry.stage("3")


if __name__ == "__main__":
    unittest.main()
