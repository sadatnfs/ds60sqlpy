"""Pure report-contract fixtures, not fabricated backend acceptance evidence."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aggregate_results import summarize
from compare_results import compare


def report(backend="native", replicate=0, status="passed"):
    row = {
        "scenario": "ordinary",
        "method": "unpenalized",
        "case_sha256": str(replicate) * 64,
        "status": status,
        "truth": [0.0],
        "canonical_initial": [0.0],
        "l2_strength": 0.0,
        "training_rows": 10,
        "future_rows": 2,
        "parameters": [1.0],
        "canonical_reference_objective": 12.0,
        "canonical_projected_score_inf": 0.0,
        "prediction_scope": "unit-test input only",
    }
    if status == "passed":
        row["future_metrics"] = {
            "future": {
                "mse": 1.0,
                "mean_marginal_nll": 2.0,
                "pointwise_coverage": 1.0,
                "unadjusted_pointwise_bands_joint_coverage": 1.0,
            }
        }
    return {
        "kind": "original-spark-modeling-study",
        "status": "completed",
        "backend": backend,
        "study": "sim-001",
        "seed": 12,
        "replicate": replicate,
        "partitions": 2,
        "fixture_sha256": "a" * 64,
        "generator_sha256": "b" * 64,
        "study_source_sha256": {"test": "c" * 64},
        "package_identity": {"version": "test"},
        "runtime_versions": {"python": "test"},
        "spark_version": "test",
        "optimizer_settings": {"test": True},
        "planned_records": [
            {
                "scenario": row["scenario"],
                "method": row["method"],
                "case_sha256": row["case_sha256"],
            }
        ],
        "records": [row],
    }


class ReportTests(unittest.TestCase):
    def test_failure_denominators_and_conditional_estimates(self):
        result = summarize(iter([report(), report(replicate=1, status="failed")]))["groups"][0]
        self.assertEqual(result["parameters"]["attempted"], 2)
        self.assertEqual(result["parameters"]["successful"], 1)
        coverage = result["future_metrics"]["future"]["pointwise_coverage"]
        self.assertEqual(coverage["conditional_on_success"]["mean"], 1.0)
        self.assertEqual(coverage["procedural_over_all_attempts"]["mean"], 0.5)
        self.assertEqual(coverage["procedural_over_all_attempts"]["mcse"], 0.5)

    def test_duplicates_missing_records_and_changed_artifacts_refuse(self):
        with self.assertRaises(ValueError):
            summarize([report(), report()])
        bad = report(replicate=1)
        bad["records"] = []
        with self.assertRaises(ValueError):
            summarize([report(), bad])
        bad = report(replicate=1)
        bad["package_identity"]["version"] = "changed"
        with self.assertRaises(ValueError):
            summarize([report(), bad])
        bad = report()
        bad["status"] = "interrupted"
        with self.assertRaises(ValueError):
            summarize([bad])

    def test_pairing_requires_same_data_and_preserves_failed_fits(self):
        native = report()
        torch = report("torch")
        compared = compare(native, torch)
        self.assertEqual(compared["records"][0]["parameter_absolute_differences"], [0.0])
        failed = report("torch", status="failed")
        self.assertIn("comparison", compare(native, failed)["records"][0])
        altered = copy.deepcopy(torch)
        altered["fixture_sha256"] = "d" * 64
        with self.assertRaises(ValueError):
            compare(native, altered)


if __name__ == "__main__":
    unittest.main()
