"""Validate bounded coverage and genuine interrupted-attempt recovery evidence."""

from __future__ import annotations

import hashlib


def partition_digest(start, end):
    digest = hashlib.sha256()
    for row_id in range(start, end):
        digest.update(row_id.to_bytes(8, "big", signed=True))
    return digest.hexdigest()


def coverage(events, token, rows, partitions):
    groups = {}
    for event in events:
        if event.get("kind") == "partition_complete" and event.get("token") == token:
            key = event["stage_id"], event["stage_attempt"]
            groups.setdefault(key, []).append(event)
    accepted = []
    for stage, records in groups.items():
        if len(records) != partitions or {r["partition_id"] for r in records} != set(
            range(partitions)
        ):
            continue
        if sum(r["rows"] for r in records) != rows:
            continue
        if sum(r["id_sum"] for r in records) != rows * (rows - 1) // 2:
            continue
        if sum(r["id_sum_squares"] for r in records) != rows * (rows - 1) * (2 * rows - 1) // 6:
            continue
        if any(
            r["id_sha256"]
            != partition_digest(
                rows * r["partition_id"] // partitions, rows * (r["partition_id"] + 1) // partitions
            )
            for r in records
        ):
            continue
        accepted.append({"stage_id": stage[0], "stage_attempt": stage[1], "partitions": records})
    if not accepted:
        raise AssertionError("No complete exact partition/row/id coverage in " + token)
    return accepted


def recovery(tasks, interrupted):
    failures = [
        e
        for e in tasks
        if e.get("kind") == "task_end"
        and e["task_id"] == interrupted["task_id"]
        and not e["successful"]
    ]
    successes = [
        e
        for e in tasks
        if e.get("kind") == "task_end"
        and e["successful"]
        and e["stage_id"] == interrupted["stage_id"]
        and e["partition_id"] == interrupted["partition_id"]
        and e["task_id"] != interrupted["task_id"]
        and e["executor_id"] != interrupted["executor_id"]
        and (
            e["attempt"] > interrupted["attempt"]
            or e["stage_attempt"] > interrupted["stage_attempt"]
        )
    ]
    if not failures or not successes:
        raise AssertionError(
            "Missing interrupted task failure and successful different-executor retry"
        )
    return {
        "interrupted_task": interrupted,
        "failed_attempts": failures,
        "successful_retries": successes,
    }


def two_workers(records):
    if len(records) != 2 or {r["host"] for r in records} != {"worker1", "worker2"}:
        raise AssertionError("Expected two distinct worker-container executor hosts")
    if len({r["executor_id"] for r in records}) != 2:
        raise AssertionError("Expected two distinct executor IDs")
    if any(r["executor_id"] == "driver" for r in records):
        raise AssertionError("Driver must not execute the worker numerical tasks")
    return records
