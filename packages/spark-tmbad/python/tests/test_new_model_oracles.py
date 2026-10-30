# SPDX-License-Identifier: MIT
import json
import struct
import sys
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))
from validate_new_model_oracles import (  # noqa: E402 - examples path is set above
    PROFILES,
    compare,
    loads,
    response_frame,
)


class RunnerTests(unittest.TestCase):
    def test_frame_rejects_truncation_and_trailing_bytes(self):
        raw = b'{"ok":true}'
        framed = struct.pack(">I", len(raw)) + raw
        self.assertEqual(response_frame(framed), {"ok": True})
        for invalid in (framed[:-1], framed + b"x", b"", b"\0\0\0\0"):
            with self.assertRaises((AssertionError, ValueError)):
                response_frame(invalid)

    def test_strict_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                loads(raw)

    def test_numerical_refusals(self):
        for actual in (True, float("inf"), float("nan"), "1", None):
            with self.assertRaises(AssertionError):
                compare(actual, "1", [3e-8, 3e-7])
        with self.assertRaises(AssertionError):
            compare([1], [1, 2], [3e-8, 3e-7])

    def test_retained_gamma_failure_is_detected(self):
        with self.assertRaises(AssertionError):
            compare(
                6.501443976958399e-6,
                "0.0000065001874528142970161952991713431856004",
                PROFILES["gamma_endpoint"]["value"],
            )

    def test_tiny_variance_cannot_round_to_zero(self):
        with self.assertRaises(AssertionError):
            compare(0.0, "9.397644082695415e-19", PROFILES["tiny_positive"]["moments"])
        compare(0.0, "2.4e-399", [3e-8, 0])

    def test_supplement_stays_in_declared_bounds(self):
        supplement = json.loads((EXAMPLES / "new_model_references/supplement-v3.json").read_text())
        self.assertEqual(len(supplement["rows"]), 9)
        self.assertEqual(len(supplement["gaussian"]), 3)
        for case in supplement["rows"]:
            self.assertTrue(-12 <= case["parameters"][0] <= 12)
            self.assertTrue(-3 <= case["parameters"][1] <= 3)
            self.assertGreaterEqual(case["rows"][0][1], 1e-6)
            self.assertGreater(float(case["value"]), 0)
            self.assertEqual(len(case["future"][0]), 2)


if __name__ == "__main__":
    unittest.main()
