"""Deterministic tests for python-perf-01."""

from __future__ import annotations

import importlib.util
import unittest

from python.professional.solutions.py_perf_01_measurement_optimization_solution import (
    BenchmarkPlan,
    benchmark,
    cached_fibonacci,
    choose_cache_policy,
    choose_native_boundary,
    choose_next_step,
    estimated_transfer_bytes,
    first_duplicate_linear,
    first_duplicate_quadratic,
    measure_peak_memory,
    numpy_sum_squares,
    profile_call,
    serialized_payload_bytes,
    sum_materialized_squares,
    sum_squares_loop,
    sum_streamed_squares,
)


class PerformanceMeasurementTests(unittest.TestCase):
    def test_algorithmic_optimization_preserves_first_duplicate_semantics(self) -> None:
        cases: list[list[int]] = [
            [],
            [1],
            [1, 2, 3],
            [4, 1, 3, 2, 3, 4],
            [9, 9, 8, 8],
            [1, 2, 1, 2],
        ]
        for values in cases:
            with self.subTest(values=values):
                self.assertEqual(
                    first_duplicate_linear(values),
                    first_duplicate_quadratic(values),
                )

    def test_timeit_report_has_bounded_shape_not_speed_threshold(self) -> None:
        report = benchmark(
            lambda: first_duplicate_linear([1, 2, 3, 2]),
            BenchmarkPlan(warmup_calls=1, repeats=3, calls_per_repeat=2),
        )
        self.assertEqual(len(report.samples_seconds), 3)
        self.assertEqual(report.calls_per_repeat, 2)
        self.assertLessEqual(report.minimum_seconds, report.median_seconds)
        self.assertLessEqual(report.median_seconds, report.maximum_seconds)
        self.assertTrue(all(sample >= 0 for sample in report.samples_seconds))

    def test_profile_report_contains_call_table_and_result(self) -> None:
        profiled = profile_call(
            lambda: first_duplicate_linear([1, 2, 3, 2]),
            rows=5,
        )
        self.assertEqual(profiled.result, 2)
        self.assertEqual(profiled.displayed_rows, 5)
        self.assertIn("function calls", profiled.report)
        self.assertIn("first_duplicate_linear", profiled.report)

    def test_tracemalloc_reports_bounds_and_equal_memory_strategies(self) -> None:
        values = list(range(500))
        materialized = measure_peak_memory(lambda: sum_materialized_squares(values))
        streamed = measure_peak_memory(lambda: sum_streamed_squares(values))
        self.assertEqual(materialized.result, streamed.result)
        for report in (materialized, streamed):
            self.assertGreaterEqual(report.current_bytes, 0)
            self.assertGreaterEqual(report.peak_bytes, report.current_bytes)

    def test_serialization_and_transfer_cost_are_explicit(self) -> None:
        payload_bytes = serialized_payload_bytes({"values": [1, 2, 3]})
        self.assertGreater(payload_bytes, 0)
        self.assertEqual(
            estimated_transfer_bytes(payload_bytes, workers=4, copies_per_worker=2),
            payload_bytes * 8,
        )
        with self.assertRaises(ValueError):
            estimated_transfer_bytes(payload_bytes, workers=0, copies_per_worker=1)

    def test_cache_and_native_boundary_policies_are_deterministic(self) -> None:
        cached_fibonacci.cache_clear()
        self.assertEqual(cached_fibonacci(10), 55)
        self.assertGreater(cached_fibonacci.cache_info().hits, 0)
        self.assertEqual(
            choose_cache_policy(
                reuse_fraction=0.8,
                estimated_entries=100,
                bytes_per_entry=20,
                memory_budget_bytes=10_000,
                freshness_required=False,
            ),
            "cache",
        )
        self.assertEqual(
            choose_cache_policy(
                reuse_fraction=0.9,
                estimated_entries=100,
                bytes_per_entry=20,
                memory_budget_bytes=10_000,
                freshness_required=True,
            ),
            "do-not-cache",
        )
        self.assertEqual(
            choose_native_boundary(
                hotspot_fraction=0.8,
                calls_across_boundary=5,
                transfer_bytes=1_000,
                algorithm_improvement_available=False,
            ),
            "batch-native-boundary",
        )
        self.assertEqual(
            choose_native_boundary(
                hotspot_fraction=0.8,
                calls_across_boundary=5,
                transfer_bytes=1_000,
                algorithm_improvement_available=True,
            ),
            "improve-algorithm",
        )

    def test_next_step_prioritizes_correctness_and_hard_bounds(self) -> None:
        self.assertEqual(
            choose_next_step(
                equivalent=False,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.2,
            ),
            "fix-correctness",
        )
        self.assertEqual(
            choose_next_step(
                equivalent=True,
                peak_bytes=2_000,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.9,
            ),
            "reduce-memory",
        )
        self.assertEqual(
            choose_next_step(
                equivalent=True,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.4,
                hotspot_fraction=0.9,
            ),
            "reduce-transfer",
        )
        self.assertEqual(
            choose_next_step(
                equivalent=True,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.8,
            ),
            "optimize-hotspot",
        )
        self.assertEqual(
            choose_next_step(
                equivalent=True,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.2,
            ),
            "keep-current",
        )


@unittest.skipUnless(
    importlib.util.find_spec("numpy") is not None,
    "NumPy is not installed; install the normal data profile",
)
class OptionalNumpyEquivalenceTests(unittest.TestCase):
    def test_vectorized_and_loop_results_match(self) -> None:
        values = [0.5, -1.0, 2.5, 4.0]
        self.assertAlmostEqual(
            numpy_sum_squares(values),
            sum_squares_loop(values),
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
