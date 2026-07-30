"""Tests for the python-pro-02 reference implementation."""

from __future__ import annotations

import asyncio
import unittest

from python.professional.solutions.py_pro_02_concurrency_parallelism_solution import (
    ConcurrencyProbe,
    bounded_map,
    choose_execution_model,
    cpu_checksum,
    delayed_square,
    deterministic_lost_update,
    run_blocking_io_in_threads,
    run_cpu_work_in_processes,
)


def exception_leaves(exception: BaseException) -> list[BaseException]:
    """Return leaf errors from an exception group."""

    if isinstance(exception, BaseExceptionGroup):
        leaves: list[BaseException] = []
        for child in exception.exceptions:
            leaves.extend(exception_leaves(child))
        return leaves
    return [exception]


class ConcurrencyDecisionTests(unittest.TestCase):
    def test_model_selection_tracks_workload_behavior(self) -> None:
        self.assertEqual(
            choose_execution_model("async-io", async_api_available=True),
            "asyncio",
        )
        self.assertEqual(
            choose_execution_model("blocking-io", async_api_available=False),
            "threads",
        )
        self.assertEqual(
            choose_execution_model("cpu", async_api_available=False),
            "processes",
        )
        with self.assertRaises(ValueError):
            choose_execution_model("cpu", async_api_available=True)

    def test_thread_pool_preserves_input_order(self) -> None:
        values = run_blocking_io_in_threads(
            [(1, 0.003), (2, 0.001), (3, 0.002)],
            max_workers=2,
        )
        self.assertEqual(values, (1, 4, 9))

    def test_lost_update_model_is_deterministic(self) -> None:
        self.assertEqual(deterministic_lost_update(10), (11, 12))

    def test_spawned_process_pool_runs_picklable_cpu_function(self) -> None:
        limits = [200, 250]
        expected = tuple(cpu_checksum(limit) for limit in limits)
        try:
            actual = run_cpu_work_in_processes(limits, max_workers=2)
        except PermissionError as exc:
            self.skipTest(f"host sandbox does not permit process-pool semaphore checks: {exc}")
        self.assertEqual(actual, expected)


class BoundedAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_queue_run_is_ordered_and_bounded(self) -> None:
        result = await bounded_map(
            [3, 1, 2, 4],
            delayed_square,
            worker_count=2,
            queue_capacity=1,
        )

        self.assertEqual(result.values, (9, 1, 4, 16))
        self.assertLessEqual(result.peak_active, 2)
        self.assertEqual(result.queue_capacity, 1)

    async def test_timeout_propagates_and_cleans_up(self) -> None:
        probe = ConcurrencyProbe()

        async def slow(value: int) -> int:
            await asyncio.sleep(0.05)
            return value

        with self.assertRaises(ExceptionGroup) as caught:
            await bounded_map(
                [1, 2, 3],
                slow,
                worker_count=2,
                queue_capacity=1,
                item_timeout=0.005,
                probe=probe,
            )

        leaves = exception_leaves(caught.exception)
        self.assertTrue(any(isinstance(error, TimeoutError) for error in leaves))
        self.assertEqual(probe.active, 0)

    async def test_worker_failure_is_not_hidden(self) -> None:
        async def worker(value: int) -> int:
            await asyncio.sleep(0)
            if value == 2:
                raise RuntimeError("expected worker failure")
            return value

        with self.assertRaises(ExceptionGroup) as caught:
            await bounded_map(
                [1, 2, 3],
                worker,
                worker_count=2,
                queue_capacity=1,
            )

        messages = [str(error) for error in exception_leaves(caught.exception)]
        self.assertIn("expected worker failure", messages)

    async def test_caller_cancellation_releases_active_work(self) -> None:
        probe = ConcurrencyProbe()

        async def slow(value: int) -> int:
            await asyncio.sleep(1)
            return value

        task = asyncio.create_task(
            bounded_map(
                [1, 2, 3],
                slow,
                worker_count=2,
                queue_capacity=1,
                probe=probe,
            )
        )
        await asyncio.sleep(0.01)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(probe.active, 0)


if __name__ == "__main__":
    unittest.main()
