"""Exercise a compiled Linux worker. No compiler or numerical Python dependency."""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import subprocess
import unittest
from pathlib import Path

BINARY = Path(os.environ["DS60_NATIVE_BINARY"])
LIMIT = 4 * 1024 * 1024


def frame(payload):
    return struct.pack(">I", len(payload)) + payload


def raw(value):
    return json.dumps(value, separators=(",", ":"), allow_nan=False).encode()


class WorkerProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [str(BINARY), "--describe"], capture_output=True, check=True, timeout=10
        )
        cls.description = json.loads(result.stdout)
        cls.models = {model["id"]: model for model in cls.description["models"]}
        cls.calls = 0

    def request(self, model="normal", **changes):
        descriptor = self.models[model]
        request = {
            "protocol": 1,
            "request_id": "native-test",
            "op": "evaluate",
            "model_id": model,
            "model_digest": descriptor["digest"],
            "theta": [0.0, 0.0],
            "rows": [[1.0]],
            "kind": "rows",
            "weights": [1.0],
        }
        request.update(changes)
        return request

    def run_bytes(self, value):
        result = subprocess.run(
            [str(BINARY), "--stdio"], input=value, capture_output=True, timeout=15
        )
        self.assertLessEqual(len(result.stderr), 8192)
        output = result.stdout
        frames = []
        while output:
            self.assertGreaterEqual(len(output), 4)
            size = struct.unpack(">I", output[:4])[0]
            self.assertLessEqual(size, LIMIT)
            self.assertGreaterEqual(len(output), size + 4)
            frames.append(json.loads(output[4 : 4 + size]))
            output = output[4 + size :]
        return result.returncode, frames

    def accept(self, request):
        payload = raw(request)
        code, responses = self.run_bytes(frame(payload))
        self.assertEqual(code, 0, responses)
        self.assertEqual(len(responses), 1)
        response = responses[0]
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["request_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(response["build_id"], self.description["build_id"])
        self.assertEqual(response["request_id"], request["request_id"])
        return response

    def refuse(self, request, error=None):
        payload = request if isinstance(request, bytes) else raw(request)
        code, responses = self.run_bytes(frame(payload))
        self.assertNotEqual(code, 0)
        self.assertEqual(len(responses), 1)
        response = responses[0]
        self.assertEqual(response["status"], "error")
        if error:
            self.assertEqual(response["error"]["code"], error)
        self.assertEqual(response["request_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertLessEqual(len(response["error"]["message"]), 512)
        return response

    def test_serial_frames_and_clean_eof(self):
        payload = raw(self.request())
        code, responses = self.run_bytes(frame(payload) * 3)
        self.assertEqual(code, 0)
        self.assertEqual(len(responses), 3)
        self.assertTrue(all(r["status"] == "ok" for r in responses))
        self.assertEqual(self.run_bytes(b""), (0, []))

    def test_failure_is_terminal_even_after_success(self):
        okay = raw(self.request())
        bad = raw(self.request(theta=[True, 0]))
        code, responses = self.run_bytes(frame(okay) + frame(bad) + frame(okay))
        self.assertNotEqual(code, 0)
        self.assertEqual([r["status"] for r in responses], ["ok", "error"])

    def test_bad_frames(self):
        for value in (
            b"\0",
            b"\0\0\0",
            struct.pack(">I", 0),
            struct.pack(">I", LIMIT + 1),
            struct.pack(">I", 100) + b"{}",
        ):
            with self.subTest(value=value):
                code, responses = self.run_bytes(value)
                self.assertNotEqual(code, 0)
                self.assertEqual(responses[0]["error"]["code"], "INVALID_FRAME")

    def test_bad_json_duplicate_utf8_surrogates_nonfinite(self):
        for value in (
            b'{"op":1,"op":2}',
            b'{"a":1,"\\u0061":2}',
            b'{"bad":"\xff"}',
            b'{"bad":"\\ud800"}',
            b'{"bad":"\\udc00"}',
            b'{"bad":NaN}',
            b'{"bad":1e999}',
            b'{"bad":01}',
            b'{"bad":1} trailing',
        ):
            with self.subTest(value=value):
                self.refuse(value, "INVALID_JSON")

    def test_structural_json_bounds(self):
        for value in (
            b"[" * 34 + b"0" + b"]" * 34,
            raw({"x": list(range(8193))}),
            raw({str(i): 0 for i in range(1025)}),
            raw({"x" * 257: 0}),
            raw({"x": "a" * 1000001}),
        ):
            self.refuse(value, "INVALID_JSON")
        # Supplementary scalars are counted once, not as four UTF-8 bytes.
        value = raw({"\U0001f600" * 256: 0})
        self.assertEqual(self.refuse(value)["error"]["code"], "INVALID_INPUT")
        self.refuse(raw({"\U0001f600" * 257: 0}), "INVALID_JSON")

    def test_integer_interchange_and_float_boundary(self):
        for value in (2**53, 2**53 + 1, -(2**53), 2**63, 10**400):
            self.refuse(self.request(theta=[value, 0]), "INVALID_JSON")
        self.accept(self.request(theta=[2**53 - 1, 0.0], rows=[[2**53 - 1]]))
        self.accept(self.request(theta=[float(2**54), 0.0], rows=[[float(2**54)]]))
        self.refuse(self.request(theta=[True, 0.0]))

    def test_identity_schema_and_undeclared_operations(self):
        for changes in (
            {"protocol": True},
            {"protocol": 1.0},
            {"model_id": "missing"},
            {"model_digest": "0" * 64},
            {"extra": "not accepted"},
            {"op": "compile"},
            {"request_id": ""},
            {"request_id": "a" * 129},
            {"request_id": "é"},
        ):
            self.refuse(self.request(**changes))
        undeclared = self.request(
            "poisson_random_slope",
            op="predict",
            theta=[0, 0, 0, 0],
            rows=[[1]],
            target="undeclared",
        )
        del undeclared["kind"], undeclared["weights"]
        self.refuse(undeclared, "UNSUPPORTED_OPERATION")

    def test_weight_dimensions_and_bounds(self):
        for changes in (
            {"weights": []},
            {"weights": [-1.0]},
            {"rows": [[1.0, 2.0]]},
            {"theta": [0.0]},
            {"theta": [0.0, 21.0]},
            {"hessian": 1},
        ):
            self.refuse(self.request(**changes))
        response = self.accept(self.request(rows=[], weights=[], hessian=True))
        self.assertEqual(response["loss"], 0)
        self.assertEqual(response["gradient"], [0, 0])
        self.assertEqual(response["hessian"], [0, 0, 0, 0])
        self.assertEqual(response["unit_count"], 0)
        response = self.accept(self.request(rows=[[1.0], [2.0]], weights=[0.0, 0.0]))
        self.assertEqual(response["gradient"], [0, 0])
        self.assertEqual(response["weight_sum"], 0)

    def unit(self, model="gaussian_random_intercept", **changes):
        result = self.request(model, theta=[0.0, 0.0, 0.0], kind="unit", unit_weight=1.0)
        del result["weights"]
        result.update(changes)
        return result

    def test_laplace_weight_and_hessian_refusal(self):
        model = "gaussian_random_intercept_laplace"
        request = self.unit(model, rows=[[1.0], [3.0], [-1.0]])
        result = self.accept(request)
        scaled = self.accept({**request, "unit_weight": 2.5})
        self.assertAlmostEqual(scaled["loss"], 2.5 * result["loss"], places=10)
        for actual, expected in zip(scaled["gradient"], result["gradient"], strict=True):
            self.assertAlmostEqual(actual, 2.5 * expected, places=10)
        self.assertEqual(scaled["unit_count"], 1)
        self.assertEqual(scaled["row_count"], 3)
        self.assertEqual(scaled["weight_sum"], 2.5)
        self.refuse({**request, "hessian": True}, "UNSUPPORTED_OPERATION")
        self.refuse({**request, "rows": []})
        self.refuse({**request, "weights": [1, 1, 1]})

    def test_count_support_and_mathematical_integer_tokens(self):
        request = self.unit("poisson_random_intercept", theta=[0.0, 0.0], rows=[[1.0, 2.0]])
        self.accept(request)
        for rows in ([[0.0, 2.0]], [[-1.0, 2.0]], [[1.0, -1.0]], [[1.0, 1.5]]):
            self.refuse({**request, "rows": rows}, "DOMAIN_ERROR")

    def test_forecast_history_cadence_and_response_absence(self):
        request = self.request(
            "ar1",
            op="forecast",
            theta=[0.0, 0.0, 0.0],
            rows=[[3.0], [4.0]],
            target="conditional_history",
            history=[[1.0, 0.0], [2.0, 1.0]],
        )
        del request["kind"], request["weights"]
        self.accept(request)
        for changes in (
            {"history": []},
            {"rows": []},
            {"rows": [[4.0], [5.0]]},
            {"rows": [[3.0], [5.0]]},
            {"history": [[0.0, 0.0], [2.0, 1.0]]},
            {"rows": [[3.0, 99.0]]},
        ):
            self.refuse({**request, **changes})
        self.accept({**request, "target": "stationary_new_series", "history": []})
        self.refuse({**request, "target": "stationary_new_series"})

    def test_custom_model_predictions_and_finite_difference_gradient(self):
        request = self.request(
            "quadratic_gaussian",
            theta=[0.4, 0.7, -0.3],
            rows=[[-1.0, 1.0], [0.5, 0.2], [2.0, 3.0]],
            weights=[1.0, 2.0, 0.5],
            hessian=True,
        )
        result = self.accept(request)
        for step in (1e-4, 1e-5):
            for j, derivative in enumerate(result["gradient"]):
                plus, minus = list(request["theta"]), list(request["theta"])
                plus[j] += step
                minus[j] -= step
                numerical = (
                    self.accept({**request, "theta": plus})["loss"]
                    - self.accept({**request, "theta": minus})["loss"]
                ) / (2 * step)
                self.assertAlmostEqual(derivative, numerical, delta=2e-6)
        prediction = {k: v for k, v in request.items() if k not in ("kind", "weights", "hessian")}
        prediction.update(op="forecast", target="response", rows=[[3.0], [4.0]], history=[])
        answer = self.accept(prediction)
        for x, row in zip((3.0, 4.0), answer["values"], strict=True):
            self.assertAlmostEqual(row[0], 0.4 + 0.7 * x * x)
            self.assertAlmostEqual(row[1], math.exp(-0.6))

    def test_new_distribution_support_and_future_hooks(self):
        fixtures = [
            (
                "bernoulli_logistic",
                [0.2, -0.3],
                [[-1.0, 1.0], [2.0, 0.0]],
                [[-1.0], [2.0]],
                [[1.0, 2.0]],
            ),
            (
                "negative_binomial2",
                [0.2, 0.1, -0.4],
                [[-1.0, 1.0, 0.0], [2.0, 0.5, 3.0]],
                [[-1.0, 1.0], [2.0, 0.5]],
                [[1.0, 1.0, 1.5]],
            ),
            (
                "gamma_regression",
                [0.2, 0.1, -0.4],
                [[-1.0, 0.4], [2.0, 3.0]],
                [[-1.0], [2.0]],
                [[1.0, 0.0]],
            ),
            (
                "saturating_growth",
                [0.2, 0.1, -0.4, -0.3],
                [[0.0, 0.4], [2.0, 3.0]],
                [[3.0], [4.0]],
                [[-1.0, 1.0]],
            ),
        ]
        for model, theta, rows, future, bad in fixtures:
            with self.subTest(model=model):
                request = self.request(
                    model, theta=theta, rows=rows, weights=[1.0, 2.0], hessian=True
                )
                result = self.accept(request)
                for step in (1e-4, 1e-5):
                    for j, derivative in enumerate(result["gradient"]):
                        plus, minus = theta.copy(), theta.copy()
                        plus[j] += step
                        minus[j] -= step
                        numerical = (
                            self.accept({**request, "theta": plus})["loss"]
                            - self.accept({**request, "theta": minus})["loss"]
                        ) / (2 * step)
                        self.assertAlmostEqual(derivative, numerical, delta=2e-6)
                self.refuse({**request, "rows": bad, "weights": [1.0]}, "DOMAIN_ERROR")
                forecast = {
                    k: v for k, v in request.items() if k not in ("kind", "weights", "hessian")
                }
                forecast.update(op="forecast", target="response", rows=future, history=[])
                observed = self.accept(forecast)
                self.assertEqual(observed["columns"], ["mean", "variance", "sd"])
                self.assertEqual(len(observed["values"]), len(future))
                self.assertTrue(all(row[1] >= 0 for row in observed["values"]))

    def test_logistic_extreme_and_nb_zero_count_stability(self):
        result = self.accept(
            self.request(
                "bernoulli_logistic",
                theta=[40.0, 0.0],
                rows=[[0.0, 1.0]],
                weights=[1.0],
                hessian=True,
            )
        )
        reference = math.log1p(math.exp(-40.0))
        self.assertGreater(result["loss"], 0)
        self.assertAlmostEqual(result["loss"] / reference, 1.0, places=12)
        self.assertAlmostEqual(
            result["gradient"][0] / (-math.exp(-40.0) / (1 + math.exp(-40.0))), 1.0, places=12
        )
        request = self.request(
            "negative_binomial2",
            theta=[-12.0, -3.0, 6.0],
            rows=[[5.0, 1e-6, 0.0]],
            weights=[1.0],
            hessian=True,
        )
        result = self.accept(request)
        reference = math.exp(6.0) * math.log1p(1e-6 * math.exp(-27.0) / math.exp(6.0))
        self.assertGreater(result["loss"], 0)
        self.assertAlmostEqual(result["loss"] / reference, 1.0, places=12)
        self.assertGreater(result["gradient"][0], 0)

    def test_two_effect_random_slope_targets(self):
        request = self.unit(
            "poisson_random_slope",
            theta=[0.2, 0.1, -0.4, -0.7],
            rows=[[-1.0, 1.0, 0.0], [0.0, 2.0, 3.0], [1.0, 0.5, 1.0]],
        )
        self.accept(request)
        future = [[-0.5, 0.7], [1.5, 2.0]]
        target_request = {k: v for k, v in request.items() if k not in ("kind", "unit_weight")}
        target_request.update(op="forecast", target="new_group", rows=future, history=[])
        result = self.accept(target_request)
        for (x, e), observed in zip(future, result["values"], strict=True):
            variance = math.exp(-0.8) + x * x * math.exp(-1.4)
            mean = e * math.exp(0.2 + 0.1 * x + 0.5 * variance)
            self.assertAlmostEqual(observed[0], mean, places=10)
            self.assertAlmostEqual(
                observed[1], mean + mean * mean * math.expm1(variance), places=10
            )
        self.accept({**target_request, "target": "existing_group", "history": request["rows"]})
        self.refuse({**target_request, "target": "existing_group"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
