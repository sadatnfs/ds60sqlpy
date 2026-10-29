"""Fast algebra and input validation; does not import R or TMB."""

import importlib.util
import math
import unittest
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parents[1] / "python" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ref, bridge = load("reference"), load("bridge")


class ReferenceTests(unittest.TestCase):
    def test_normal_gradient(self):
        y, theta = [1.0, 2.0, 4.0, 7.0], [2.2, 0.3]
        value, gradient = ref.gaussian_value_gradient(y, *theta)
        self.assertTrue(math.isfinite(value))
        for j in range(2):
            plus, minus = theta.copy(), theta.copy()
            plus[j] += 1e-5
            minus[j] -= 1e-5
            numeric = (
                ref.gaussian_value_gradient(y, *plus)[0] - ref.gaussian_value_gradient(y, *minus)[0]
            ) / 2e-5
            self.assertAlmostEqual(numeric, gradient[j], places=6)

    def test_normal_mle(self):
        y = [1.0, 2.0, 4.0, 7.0]
        mu = sum(y) / len(y)
        sigma = math.sqrt(sum((x - mu) ** 2 for x in y) / len(y))
        self.assertLess(
            max(map(abs, ref.gaussian_value_gradient(y, mu, math.log(sigma))[1])), 1e-12
        )

    def test_censoring(self):
        self.assertAlmostEqual(
            ref.weibull_nll([2.0, 4.0], [0.0, 1.0], [1, 0], 2.0, 1.0), 2.5 + math.log(2)
        )
        with self.assertRaises(ValueError):
            ref.weibull_nll([1.0], [1.0], [0], 1, 1)

    def test_ar1_precision(self):
        for phi in [-0.7, 0, 0.8]:
            n, tau = 5, 1.3
            q = ref.ar1_precision(n, phi, tau)
            cov = [[tau * tau * phi ** abs(i - j) for j in range(n)] for i in range(n)]
            for i in range(n):
                for j in range(n):
                    self.assertAlmostEqual(
                        sum(q[i][k] * cov[k][j] for k in range(n)), float(i == j), places=12
                    )
        self.assertEqual(ref.ar1_precision(1, 0.4, 2), [[0.25]])

    def test_laplace_normal_integrates_to_one(self):
        tau = 1.7
        f = math.log(tau) + 0.5 * math.log(2 * math.pi)
        self.assertAlmostEqual(ref.gaussian_laplace(f, 1 / tau**2, 1), 0)

    def test_coupled_determinant(self):
        self.assertNotEqual(math.log(4 - 0.8**2), 2 * math.log(2))

    def test_row_contract(self):
        rows = [{"row_id": f"r{i}", "x": float(i), "y": 2.0 * i} for i in range(3)]
        self.assertEqual(bridge.validate_rows(rows), rows)
        for bad in [
            dict(rows[0], row_id="r1"),
            dict(rows[0], y=float("nan")),
            dict(rows[0], x=True),
            dict(rows[0], y=None),
        ]:
            with self.assertRaises(ValueError):
                bridge.validate_rows([bad, *rows[1:]])

    def test_rank_deficient_bridge(self):
        with self.assertRaises(ValueError):
            bridge.validate_rows([{"row_id": str(i), "x": 1.0, "y": float(i)} for i in range(4)])


if __name__ == "__main__":
    unittest.main()
