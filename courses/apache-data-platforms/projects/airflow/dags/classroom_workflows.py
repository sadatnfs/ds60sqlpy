"""Finite real TaskFlow workflows for the owned local installation."""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import pendulum
from airflow.sdk import Asset, Connection, dag, get_current_context, task
from airflow.timetables.interval import CronDataIntervalTimetable
from project_data import (
    DAYS,
    ROOT,
    atomic,
    capture_source,
    read_snapshot,
    validate_interval,
    write_partition,
)

ORDERS = Asset("x-classroom://orders/daily")


@dag(
    dag_id="classroom_orders",
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="UTC"),
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    end_date=pendulum.datetime(2026, 1, 2, 23, 59, tz="UTC"),
    catchup=True,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["classroom", "finite-fixture"],
)
def orders_workflow():
    @task(retries=1, retry_delay=timedelta(seconds=1), execution_timeout=timedelta(seconds=30))
    def fail_once():
        context = get_current_context()
        day = validate_interval(
            str(context["data_interval_start"]), str(context["data_interval_end"])
        )
        identity = hashlib.sha256(context["run_id"].encode()).hexdigest()
        marker = ROOT / "attempts" / (identity + ".json")
        if not marker.exists():
            with marker.open("x") as handle:
                json.dump({"run_id": context["run_id"], "intentional_first_failure": True}, handle)
            raise RuntimeError("Intentional fixture failure: the configured retry should proceed")
        if (
            marker.is_symlink()
            or marker.stat().st_size > 4096
            or json.loads(marker.read_text())["run_id"] != context["run_id"]
        ):
            raise ValueError("Unexpected retry marker")
        return day

    @task(outlets=[ORDERS], execution_timeout=timedelta(seconds=30))
    def write(day: str):
        context = get_current_context()
        if day not in DAYS:
            raise ValueError("Interval outside the finite fixture")
        return write_partition(day, 0, context["run_id"])

    write(fail_once())


@dag(
    dag_id="classroom_correction",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["classroom", "manual-correction"],
)
def correction_workflow():
    @task(outlets=[ORDERS], execution_timeout=timedelta(seconds=30))
    def correct():
        context = get_current_context()
        conf = context["dag_run"].conf or {}
        if conf != {"day": DAYS[0]}:
            raise ValueError("Expected the one explicitly allowed correction day")
        return write_partition(DAYS[0], 1, context["run_id"])

    correct()


@dag(
    dag_id="classroom_asset_consumer",
    schedule=[ORDERS],
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["classroom", "asset-mapping"],
)
def asset_workflow():
    @task(execution_timeout=timedelta(seconds=30))
    def select_source():
        return capture_source(get_current_context()["run_id"])

    @task(pool="classroom_io", execution_timeout=timedelta(seconds=30))
    def summarize(region: str, snapshot: dict[str, str]):
        if region not in ("east", "west"):
            raise ValueError("Unknown mapped region")
        context = get_current_context()
        captured = read_snapshot(snapshot)
        rows = [row for row in captured["rows"] if row["region"] == region]
        observation = {
            "run_id": context["run_id"],
            "region": region,
            "source_versions": captured["source_versions"],
            "rows": len(rows),
            "amount_total": sum(row["amount"] for row in rows),
        }
        identity = hashlib.sha256(context["run_id"].encode()).hexdigest()
        atomic(ROOT / "summaries" / (identity + "-" + region + ".json"), observation)
        return {"region": region, "rows": len(rows)}

    summarize.partial(snapshot=select_source()).expand(region=["east", "west"])


@dag(
    dag_id="classroom_connections",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["classroom", "runtime-connections"],
)
def connection_workflow():
    @task(execution_timeout=timedelta(seconds=30))
    def inspect_reference():
        reference = Connection.get("classroom_fixture")
        if reference.conn_type != "generic" or reference.extra_dejson.get("dataset") != "orders":
            raise ValueError("Unexpected local connection contract")
        try:
            Connection.get("classroom_intentionally_missing")
        except Exception as error:
            text = str(error).lower()
            if not any(
                token in text for token in ("not found", "not_found", "isn't defined", "notfound")
            ):
                raise AssertionError("Unexpected missing-connection error category") from error
            missing_type = type(error).__name__
        else:
            raise AssertionError("Absent connection unexpectedly resolved")
        if Connection.get("classroom_fixture").conn_type != "generic":
            raise AssertionError("Known connection changed")
        result = {
            "known_reference_resolved": True,
            "missing_reference_rejected": True,
            "missing_error_type": missing_type,
            "credential_values_recorded": False,
        }
        atomic(ROOT / "observations" / "connections.json", result)
        return result

    inspect_reference()


orders_workflow()
correction_workflow()
asset_workflow()
connection_workflow()
