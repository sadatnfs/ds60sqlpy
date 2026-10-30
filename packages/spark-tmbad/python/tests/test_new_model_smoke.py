"""Pure checks of reference selection and fixture contracts, without Spark/native."""

import copy
import json
import math
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))
import validate_new_models as smoke

REFERENCE_ROOT = EXAMPLES / "new_model_references"
ROWS = REFERENCE_ROOT / "rows-v3.json"
GAUSSIAN = REFERENCE_ROOT / "gaussian-v3.json"


class MetadataRuntime:
    def __init__(self, descriptor):
        self.value = descriptor

    def descriptor(self, model_id):
        return self.value


def metadata_descriptor(model_id):
    correlated = model_id == smoke.CORRELATED
    fields = ["x", "y"] if correlated else smoke.ROW_FIELDS[model_id]
    names = ["existing_group", "new_group"] if correlated else ["response"]
    targets = {
        name: {
            "fields": fields[:-1],
            "columns": smoke.MOMENT_COLUMNS,
            "needs_history": name == "existing_group",
        }
        for name in names
    }
    return {
        "fit_fields": fields,
        "fit_kind": "unit" if correlated else "rows",
        "ordered": False,
        "predict": targets,
        "forecast": copy.deepcopy(targets),
    }


class NewModelSmokeContracts(unittest.TestCase):
    def test_receipt_requires_fresh_path_and_preserves_completed_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            smoke.write_receipt(path, {"status": "running", "cases": []}, create=True)
            with self.assertRaises(FileExistsError):
                smoke.write_receipt(path, {"status": "running", "cases": []}, create=True)
            smoke.write_receipt(path, {"status": "failed", "cases": [{"case": "completed"}]})
            self.assertEqual(
                json.loads(path.read_text()),
                {"status": "failed", "cases": [{"case": "completed"}]},
            )
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def test_invalid_receipt_update_keeps_last_durable_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            smoke.write_receipt(path, {"status": "running", "cases": []}, create=True)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                smoke.write_receipt(path, {"value": float("nan")})
            self.assertEqual(path.read_bytes(), before)

    def test_retained_reference_bytes(self):
        self.assertEqual(
            smoke.sha256(ROWS),
            "711b813b5069cbaee4abfc30b8132267ce3478ef70cc8919912d0243c27957cd",
        )
        self.assertEqual(
            smoke.sha256(GAUSSIAN),
            "34a583886fdd2cb0670f80c194141bc397e3dccfad61d56b40d9f4e4d264b9cc",
        )

    def test_two_parameter_points_per_model(self):
        cases = smoke.selected_cases(ROWS, GAUSSIAN)
        self.assertEqual(len(cases), 18)
        self.assertEqual(
            Counter(model for model, _, _ in cases),
            {model: 2 for model in [*smoke.ROW_FIELDS, smoke.CORRELATED]},
        )

    def test_response_free_future_and_identity(self):
        for model, case, _ in smoke.selected_cases(ROWS, GAUSSIAN):
            with self.subTest(model=model, case=case["case"]):
                training, future = smoke.fixture_rows(model, case)
                self.assertTrue(all("y" in row for row in training))
                self.assertTrue(all("y" not in row for row in future))
                self.assertEqual(
                    [row["row_id"] for row in future],
                    list(range(100, 100 + len(future))),
                )
                self.assertIn("CAST(`row_id` AS BIGINT)", smoke.fixture_sql(future))
                self.assertNotIn("`y`", smoke.fixture_sql(future))

    def test_weights_and_complete_unit_layout(self):
        for model, case, _ in smoke.selected_cases(ROWS, GAUSSIAN):
            with self.subTest(model=model, case=case["case"]):
                training, future = smoke.fixture_rows(model, case)
                if model == smoke.CORRELATED:
                    self.assertTrue(all(row["series"] == "g0" for row in training + future))
                    self.assertTrue(all("weight" not in row for row in training))
                else:
                    self.assertEqual([row["weight"] for row in training], case["weights"])
                    self.assertTrue(all("series" not in row for row in training + future))

    def test_reference_moment_shapes_and_nonnegative_variance(self):
        for model, case, _ in smoke.selected_cases(ROWS, GAUSSIAN):
            targets = ["existing_group", "new_group"] if model == smoke.CORRELATED else ["response"]
            for target in targets:
                values = smoke.moments(case, target)
                self.assertEqual(len(values), len(case["future"]))
                for mean, variance, sd in values:
                    self.assertTrue(all(math.isfinite(value) for value in (mean, variance, sd)))
                    self.assertGreaterEqual(variance, 0)
                    self.assertAlmostEqual(sd * sd / max(variance, 1), variance / max(variance, 1))

    def test_correlated_targets_use_distinct_conditional_moments(self):
        for model, case, _ in smoke.selected_cases(ROWS, GAUSSIAN):
            if model == smoke.CORRELATED:
                existing = smoke.moments(case, "existing_group")
                new = smoke.moments(case, "new_group")
                self.assertNotEqual(existing, new)
                self.assertTrue(all(a[1] < b[1] for a, b in zip(existing, new, strict=True)))

    def test_descriptors_admit_all_nine_shapes(self):
        for model in [*smoke.ROW_FIELDS, smoke.CORRELATED]:
            smoke.descriptor_check(MetadataRuntime(metadata_descriptor(model)), model)

    def test_descriptor_rejects_response_in_future_fields(self):
        descriptor = metadata_descriptor("beta_binomial")
        descriptor["predict"]["response"]["fields"] = ["x", "trials", "y"]
        with self.assertRaisesRegex(AssertionError, "unexpected fields"):
            smoke.descriptor_check(MetadataRuntime(descriptor), "beta_binomial")

    def test_descriptor_rejects_wrong_factorization(self):
        descriptor = metadata_descriptor(smoke.CORRELATED)
        descriptor["fit_kind"] = "rows"
        with self.assertRaisesRegex(AssertionError, "factorization"):
            smoke.descriptor_check(MetadataRuntime(descriptor), smoke.CORRELATED)

    def test_descriptor_rejects_missing_variance(self):
        descriptor = metadata_descriptor("beta_regression")
        descriptor["forecast"]["response"]["columns"] = ["mean", "sd"]
        with self.assertRaisesRegex(AssertionError, "moment columns"):
            smoke.descriptor_check(MetadataRuntime(descriptor), "beta_regression")

    def test_numeric_comparison_fails_closed(self):
        for value in (True, False, float("nan"), float("inf"), "1"):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                smoke.close(value, 1)
        with self.assertRaises(AssertionError):
            smoke.close(1.1, 1)
        smoke.close(1, 1)

    def test_sql_rejects_nonfinite_or_misaligned_values(self):
        for rows in ([], [{"x": float("nan")}], [{"x": 1}, {"y": 2}], [{"x": True}]):
            with self.subTest(rows=rows), self.assertRaises(AssertionError):
                smoke.fixture_sql(rows)


if __name__ == "__main__":
    unittest.main()
