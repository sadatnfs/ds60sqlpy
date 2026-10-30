"""Independent tiny dense validation of global Gaussian sufficient statistics."""

from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from global_gaussian import (
    NumericalCertificateError,
    cholesky,
    combine,
    dense_oracle,
    dot,
    evaluate,
    matmul,
    matvec,
    solve_cholesky,
    summarize,
    transpose,
)
from study_support import normal


def rows():
    result = []
    for i in range(12):
        x = -1.0 + 2 * i / 11
        z = [math.sin(math.pi * x), math.cos(math.pi * x)]
        y = 0.3 + 0.8 * x + 0.7 * z[0] - 0.4 * z[1] + 0.5 * normal(123, "global", i)
        result.append({"row_id": i, "x": [1.0, x], "z": z, "y": y})
    return result


class GlobalGaussianTests(unittest.TestCase):
    def test_partition_merge_and_dense_value_gradient_oracles(self):
        data = rows()
        base = [[1.0, 0.25], [0.25, 1.4]]
        snapshot = summarize(0, data, 2, 2)
        layouts = [[data], [data[:3], [], data[3:]], [data[::3], data[1::3], data[2::3], []]]
        for layout in layouts:
            stats = combine(
                [summarize(i, part, 2, 2) for i, part in enumerate(layout)],
                expected_partitions=len(layout),
                expected_rows=len(data),
                expected_ledger=snapshot["ledger"],
            )
            for theta in (
                [0.2, 0.7, math.log(0.6), math.log(0.9)],
                [-0.5, 0.3, math.log(1.1), math.log(0.4)],
            ):
                actual = evaluate(stats, theta, base)
                self.assertAlmostEqual(actual["value"], dense_oracle(data, theta, base), places=10)
                for step in (1e-4, 1e-5):
                    for j in range(len(theta)):
                        plus, minus = list(theta), list(theta)
                        plus[j] += step
                        minus[j] -= step
                        score = (
                            dense_oracle(data, plus, base) - dense_oracle(data, minus, base)
                        ) / (2 * step)
                        self.assertAlmostEqual(actual["gradient"][j], score, delta=2e-6)

    def test_conditional_latent_moments_against_dense_conditioning(self):
        data = rows()
        base = [[1.0, 0.25], [0.25, 1.4]]
        theta = [0.2, 0.7, math.log(0.6), math.log(0.9)]
        stats = summarize(0, data, 2, 2)
        actual = evaluate(stats, theta, base)
        s, t = 0.6**2, 0.9**2
        n = len(data)
        z = [r["z"] for r in data]
        v = [
            [s * float(i == j) + t * dot(z[i], matvec(base, z[j])) for j in range(n)]
            for i in range(n)
        ]
        factor = cholesky(v)
        residual = [r["y"] - dot(r["x"], theta[:2]) for r in data]
        mean = [t * x for x in matvec(base, matvec(transpose(z), solve_cholesky(factor, residual)))]
        vinvz = transpose([solve_cholesky(factor, column) for column in transpose(z)])
        correction = matmul(matmul(base, matmul(transpose(z), vinvz)), base)
        covariance = [
            [t * base[i][j] - t * t * correction[i][j] for j in range(2)] for i in range(2)
        ]
        for a, b in zip(actual["latent_conditional_mean"], mean, strict=True):
            self.assertAlmostEqual(a, b, places=11)
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(
                    actual["latent_conditional_covariance"][i][j], covariance[i][j], places=11
                )

    def test_independent_partition_marginals_are_a_different_model(self):
        data = rows()
        theta = [0.2, 0.7, math.log(0.6), math.log(0.9)]
        base = [[1.0, 0.25], [0.25, 1.4]]
        global_loss = evaluate(summarize(0, data, 2, 2), theta, base)["value"]
        independent = math.fsum(
            evaluate(summarize(i, part, 2, 2), theta, base)["value"]
            for i, part in enumerate([data[:6], data[6:]])
        )
        self.assertGreater(abs(global_loss - independent), 0.01)

    def test_missing_duplicate_stale_and_corrupted_partitions_refuse(self):
        data = rows()
        snapshot = summarize(0, data, 2, 2)
        first, last = summarize(0, data[:3], 2, 2), summarize(1, data[3:], 2, 2)
        for parts in ([first], [first, first]):
            with self.assertRaises(ValueError):
                combine(
                    parts,
                    expected_partitions=2,
                    expected_rows=12,
                    expected_ledger=snapshot["ledger"],
                )
        changed = copy.deepcopy(data[3:])
        changed[0]["y"] += 0.1
        with self.assertRaises(ValueError):
            combine(
                [first, summarize(1, changed, 2, 2)],
                expected_partitions=2,
                expected_rows=12,
                expected_ledger=snapshot["ledger"],
            )
        empty = summarize(2, [], 2, 2)
        empty["gram"][0][0] = 1
        with self.assertRaises(ValueError):
            combine(
                [first, last, empty],
                expected_partitions=3,
                expected_rows=12,
                expected_ledger=snapshot["ledger"],
            )

    def test_nonpositive_covariance_and_cancellation_fail_without_jitter(self):
        data = rows()
        stats = summarize(0, data, 2, 2)
        theta = [0.2, 0.7, 0.0, 0.0]
        with self.assertRaises(ValueError):
            evaluate(stats, theta, [[1.0, 2.0], [2.0, 1.0]])
        # At an exactly fitted intercept raw cross products cannot independently
        # certify whether a zero residual is exact or cancellation. Fail closed.
        exact = [{"row_id": i, "x": [1.0], "z": [float(i)], "y": 1e8} for i in range(4)]
        with self.assertRaises(NumericalCertificateError):
            evaluate(summarize(0, exact, 1, 1), [1e8, 0.0, 0.0], [[1.0]])
        with self.assertRaises(ValueError):
            dense_oracle(data * 6, theta, [[1.0, 0.0], [0.0, 1.0]])


if __name__ == "__main__":
    unittest.main()
