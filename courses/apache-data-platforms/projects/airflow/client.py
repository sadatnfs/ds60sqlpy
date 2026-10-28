"""Observe actual local Airflow metadata and bounded source-bound outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time

from airflow.models.dag import DagModel
from airflow.models.dagrun import DagRun
from airflow.models.pool import Pool
from airflow.models.taskinstance import TaskInstance
from airflow.utils.session import create_session
from health import check
from project_data import DAYS, ROOT, read_partition, validate_interval, validate_summary

DAGS = (
    "classroom_orders",
    "classroom_correction",
    "classroom_asset_consumer",
    "classroom_connections",
)


def metadata() -> dict[str, object]:
    with create_session() as session:
        runs = session.query(DagRun).filter(DagRun.dag_id.in_(DAGS)).all()
        tasks = session.query(TaskInstance).filter(TaskInstance.dag_id.in_(DAGS)).all()
        pool = session.query(Pool).filter(Pool.pool == "classroom_io").one_or_none()
        if len(runs) > 32 or len(tasks) > 128:
            raise ValueError("Metadata exceeds finite fixture bounds")
        return {
            "runs": [
                {
                    "dag_id": row.dag_id,
                    "run_id": row.run_id,
                    "state": str(row.state),
                    "logical_date": str(row.logical_date),
                    "run_after": str(row.run_after),
                    "interval_start": str(row.data_interval_start),
                    "interval_end": str(row.data_interval_end),
                }
                for row in runs
            ],
            "tasks": [
                {
                    "dag_id": row.dag_id,
                    "run_id": row.run_id,
                    "task_id": row.task_id,
                    "state": str(row.state),
                    "try_number": row.try_number,
                    "map_index": row.map_index,
                }
                for row in tasks
            ],
            "pool_slots": None if pool is None else pool.slots,
        }


def cli(*arguments: str) -> None:
    result = subprocess.run(["airflow", *arguments], capture_output=True, text=True, timeout=40)
    if result.returncode:
        raise RuntimeError(
            "Airflow command failed: "
            + " ".join(arguments[:3])
            + "\n"
            + (result.stdout + result.stderr)[-3000:]
        )


def discovered() -> None:
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        with create_session() as session:
            names = {
                row.dag_id
                for row in session.query(DagModel).filter(DagModel.dag_id.in_(DAGS)).all()
            }
        if names == set(DAGS):
            return
        time.sleep(2)
    raise TimeoutError("Finite DAGs were not discovered; inspect import errors and processor logs")


def wait(dag_id: str, count: int = 1) -> dict[str, object]:
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        state = metadata()
        runs = [row for row in state["runs"] if row["dag_id"] == dag_id]
        if any(row["state"] == "failed" for row in runs):
            raise RuntimeError("Known workflow failed; inspect its actual task logs")
        if len([row for row in runs if row["state"] == "success"]) >= count:
            return state
        time.sleep(2)
    raise TimeoutError("Workflow did not finish within its bounded deadline")


def trigger(dag_id: str, run_id: str, conf: dict[str, str] | None = None) -> None:
    cli("dags", "unpause", dag_id)
    if not any(row["dag_id"] == dag_id and row["run_id"] == run_id for row in metadata()["runs"]):
        arguments = ["dags", "trigger", "--run-id", run_id]
        if conf is not None:
            arguments.extend(["--conf", json.dumps(conf)])
        cli(*arguments, dag_id)


def run_intervals() -> dict[str, object]:
    cli("dags", "unpause", "classroom_orders")
    result = wait("classroom_orders", 2)
    runs = [row for row in result["runs"] if row["dag_id"] == "classroom_orders"]
    actual_days = {validate_interval(row["interval_start"], row["interval_end"]) for row in runs}
    if len(runs) != 2 or actual_days != set(DAYS):
        raise AssertionError("Actual scheduled intervals differ from the two-day contract")
    for day in DAYS:
        read_partition(day)
    return result


def readback() -> dict[str, object]:
    state = metadata()
    state["outputs"] = [
        read_partition(day) for day in DAYS if (ROOT / "outputs" / (day + ".json")).exists()
    ]
    observations = {}
    for folder in ("summaries", "observations", "write-receipts", "snapshots"):
        paths = sorted((ROOT / folder).glob("*.json"))
        if len(paths) > 64 or any(p.is_symlink() or p.stat().st_size > 16_384 for p in paths):
            raise ValueError("Saved observation bounds exceeded")
        observations[folder] = [json.loads(p.read_text()) for p in paths]
        if folder == "summaries":
            for record in observations[folder]:
                validate_summary(record)
    state["saved_observations"] = observations
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "health",
            "readback",
            "run-intervals",
            "retry-check",
            "backfill-check",
            "asset-check",
            "connection-check",
        ],
    )
    action = parser.parse_args().action
    if action == "health":
        print(json.dumps(check(), indent=2))
        return
    if action == "readback":
        print(json.dumps(readback(), indent=2))
        return
    discovered()
    if action == "run-intervals":
        result = run_intervals()
    elif action == "retry-check":
        result = run_intervals()
        attempts = [
            row
            for row in result["tasks"]
            if row["dag_id"] == "classroom_orders" and row["task_id"] == "fail_once"
        ]
        if len(attempts) != 2 or any(
            row["state"] != "success" or row["try_number"] < 2 for row in attempts
        ):
            raise AssertionError("Actual retry metadata does not show the expected second attempt")
    elif action == "backfill-check":
        run_intervals()
        second = (ROOT / "outputs" / (DAYS[1] + ".json")).read_bytes()
        trigger("classroom_correction", "classroom-correction-v1", {"day": DAYS[0]})
        result = wait("classroom_correction")
        if read_partition(DAYS[0])["amount_total"] != 15:
            raise AssertionError("Corrected partition differs")
        if (ROOT / "outputs" / (DAYS[1] + ".json")).read_bytes() != second:
            raise AssertionError("Unrelated partition changed")
        result["unchanged_second_sha256"] = hashlib.sha256(second).hexdigest()
    elif action == "asset-check":
        cli("dags", "unpause", "classroom_asset_consumer")
        run_intervals()
        result = wait("classroom_asset_consumer")
        mapped = [
            row
            for row in result["tasks"]
            if row["dag_id"] == "classroom_asset_consumer"
            and row["task_id"] == "summarize"
            and row["state"] == "success"
        ]
        if {row["map_index"] for row in mapped} != {0, 1} or result["pool_slots"] != 1:
            raise AssertionError("Actual mapped task or pool metadata differs")
    else:
        trigger("classroom_connections", "classroom-connections-v1")
        result = wait("classroom_connections")
        observation = json.loads((ROOT / "observations/connections.json").read_text())
        if (
            observation.get("known_reference_resolved") is not True
            or observation.get("missing_reference_rejected") is not True
        ):
            raise AssertionError("Connection observations differ")
    if action == "asset-check":
        expected_versions = {day: read_partition(day)["source_sha256"] for day in DAYS}
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            observed = readback()
            completed = {
                row["run_id"]
                for row in observed["runs"]
                if row["dag_id"] == "classroom_asset_consumer" and row["state"] == "success"
            }
            summaries = observed["saved_observations"]["summaries"]
            matches = {
                run_id
                for run_id in completed
                if {
                    row["region"]
                    for row in summaries
                    if row["run_id"] == run_id and row["source_versions"] == expected_versions
                }
                == {"east", "west"}
            }
            if matches:
                result = observed
                result["verified_current_source_runs"] = sorted(matches)
                break
            time.sleep(2)
        else:
            raise TimeoutError(
                "Asset consumer did not reconcile both regions against current source versions"
            )
    result["passed"] = True
    result["actual_airflow"] = True
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
