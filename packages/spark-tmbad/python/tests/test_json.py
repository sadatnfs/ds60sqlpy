"""Data contract checks. These tests do not execute Spark."""

import math
import tempfile
import unittest
from pathlib import Path

from ds60_spark_tmbad._json import ContractError, copy_object, dumps, loads, read


class JsonContractTests(unittest.TestCase):
    def test_valid_json_round_trip_is_independent(self):
        original = {"theta": [1.25, -3.0], "spec": {"modelId": "normal"}}
        copied = copy_object(original)
        original["theta"].append(5.0)
        self.assertEqual(copied["theta"], [1.25, -3.0])
        self.assertEqual(loads(dumps(copied)), copied)

    def test_duplicate_keys_are_rejected_at_any_depth(self):
        for raw in ('{"a":1,"a":2}', '{"a":{"x":1,"x":2}}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ContractError, "Duplicate"):
                loads(raw)

    def test_nonfinite_values_are_rejected(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaisesRegex(ContractError, "finite"):
                dumps({"theta": [value]})
        for token in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(token=token), self.assertRaises(ContractError):
                loads('{"theta":[' + token + "]}")

    def test_only_json_objects_and_exact_numbers_cross_boundary(self):
        invalid = ({1: "x"}, {"x": object()}, {"x": (1, 2)}, {"x": 2**53})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ContractError):
                dumps(value)
        for raw in ("[]", "null", "1", b"\xff"):
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                loads(raw)

    def test_large_and_deep_documents_are_rejected(self):
        with self.assertRaisesRegex(ContractError, "size"):
            loads('{"x":"' + "a" * (4 * 1024 * 1024) + '"}')
        with self.assertRaisesRegex(ContractError, "depth"):
            loads('{"x":' + "[" * 50 + "0" + "]" * 50 + "}")

    def test_utf16_and_unpaired_surrogates_are_rejected(self):
        with self.assertRaisesRegex(ContractError, "UTF-8"):
            loads('{"x":1}'.encode("utf-16"))
        with self.assertRaisesRegex(ContractError, "Unicode"):
            loads('{"x":"\\ud800"}')
        with self.assertRaisesRegex(ContractError, "Unicode"):
            dumps({"\ud800": 1})

    def test_structural_limits_match_the_native_and_jvm_contract(self):
        for value, message in (
            ({str(index): 0 for index in range(1025)}, "field count"),
            ({"x": [0] * 8193}, "element count"),
            ({"x" * 257: 0}, "key"),
            ({"x": "y" * 1_000_001}, "string"),
        ):
            with self.subTest(message=message), self.assertRaisesRegex(ContractError, message):
                dumps(value)
        # Each non-BMP symbol is one Unicode scalar, despite two UTF-16 code units.
        key = "\U0001f642" * 256
        self.assertEqual(loads(dumps({key: 1})), {key: 1})
        value = "\U0001f642" * 400_000
        raw = dumps({"x": value})
        self.assertLess(len(raw.encode("utf-8")), 4 * 1024 * 1024)
        self.assertEqual(loads(raw)["x"], value)

    def test_file_reads_are_bounded_and_data_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            path.write_text('{"module":"os","callable":"system"}', encoding="utf-8")
            self.assertEqual(read(path), {"module": "os", "callable": "system"})
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ContractError):
                read(path)


if __name__ == "__main__":
    unittest.main()
