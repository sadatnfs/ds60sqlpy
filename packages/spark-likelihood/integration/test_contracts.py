"""Evidence validators reject partial coverage and pretend recovery claims."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "integration_validate", Path(__file__).with_name("validate.py")
)
assert SPEC is not None and SPEC.loader is not None
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class EvidenceContracts(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "kind": "partition_complete",
                "token": "loss",
                "stage_id": 2,
                "stage_attempt": 0,
                "partition_id": 0,
                "rows": 2,
                "id_sum": 1,
                "id_sum_squares": 1,
            },
            {
                "kind": "partition_complete",
                "token": "loss",
                "stage_id": 2,
                "stage_attempt": 0,
                "partition_id": 1,
                "rows": 2,
                "id_sum": 5,
                "id_sum_squares": 13,
            },
        ]
        for row in self.records:
            row["id_sha256"] = validate.partition_digest(
                row["partition_id"] * 2, (row["partition_id"] + 1) * 2
            )
        self.interrupted = {
            "task_id": 10,
            "stage_id": 2,
            "stage_attempt": 0,
            "partition_id": 1,
            "attempt": 0,
            "executor_id": "1",
        }
        self.failed = {**self.interrupted, "kind": "task_end", "successful": False}
        self.retried = {
            **self.interrupted,
            "kind": "task_end",
            "successful": True,
            "attempt": 1,
            "task_id": 12,
            "executor_id": "0",
        }

    def test_complete_coverage_accepts_all_rows_and_partitions(self):
        self.assertEqual(len(validate.coverage(self.records, "loss", 4, 2)), 1)

    def test_missing_or_duplicate_partition_is_rejected(self):
        for records in [self.records[:1], [self.records[0], self.records[0]], self.records * 2]:
            with self.assertRaises(AssertionError):
                validate.coverage(records, "loss", 4, 2)

    def test_row_identity_mismatch_is_rejected_even_when_count_matches(self):
        records = copy.deepcopy(self.records)
        for field, value in [("id_sum_squares", 12), ("id_sha256", "0" * 64)]:
            records[1][field] = value
            with self.assertRaises(AssertionError):
                validate.coverage(records, "loss", 4, 2)

    def test_actual_failed_attempt_and_other_executor_retry_are_required(self):
        observed = validate.recovery([self.failed, self.retried], self.interrupted)
        self.assertEqual(observed["successful_retries"][0]["task_id"], 12)
        for events in [
            [self.failed],
            [self.retried],
            [self.failed, {**self.retried, "executor_id": "1"}],
            [self.failed, {**self.retried, "partition_id": 0}],
            [self.failed, {**self.retried, "attempt": 0}],
        ]:
            with self.assertRaises(AssertionError):
                validate.recovery(events, self.interrupted)

    def test_two_worker_containers_are_distinct_from_driver_or_same_host(self):
        records = [
            {"host": "worker1", "executor_id": "0", "pid": 80},
            {"host": "worker2", "executor_id": "1", "pid": 80},
        ]
        self.assertEqual(validate.two_workers(records), records)
        for altered in [
            {**records[1], "host": "worker1"},
            {**records[1], "executor_id": "0"},
            {**records[1], "executor_id": "driver"},
        ]:
            with self.assertRaises(AssertionError):
                validate.two_workers([records[0], altered])


if __name__ == "__main__":
    unittest.main()
