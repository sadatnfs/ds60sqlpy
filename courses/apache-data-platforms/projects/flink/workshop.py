"""Fixed actual Flink requests, bounded REST observation and retained receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import signal
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from project_state import (
    ROOT,
    SOURCE,
    atomic_json,
    initialize,
    result_rows,
    source_code_identity,
    verify_result,
)

REST = "http://jobmanager:8081"
FLINK = "/opt/flink/bin/flink"
TERMINAL = {"FINISHED", "FAILED", "CANCELED", "SUSPENDED"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Unexpected redirect from the private Flink endpoint")


def api(path: str) -> Any:
    if not path.startswith("/") or ".." in path:
        raise ValueError("Unexpected fixed REST path")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(REST + path, timeout=5) as response:
        raw = response.read(256_001)
    if len(raw) > 256_000:
        raise ValueError("Flink REST response exceeds its budget")
    return json.loads(raw)


def health(task: bool = False) -> dict:
    result = api("/overview")
    if result.get("flink-version") != "2.3.0":
        raise ValueError("Actual Flink REST version differs from the prepared contract")
    if task and (result.get("taskmanagers") != 1 or result.get("slots-total") != 2):
        raise ValueError("The expected actual TaskManager/two slots are not registered")
    return {
        "passed": True,
        "actual_flink_version": result["flink-version"],
        "taskmanagers": result.get("taskmanagers"),
        "slots_total": result.get("slots-total"),
    }


def process(arguments: list[str], timeout: int = 120) -> tuple[int, str]:
    child = subprocess.Popen(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        import os

        os.killpg(child.pid, signal.SIGTERM)
        try:
            output, _ = child.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            output, _ = child.communicate()
        raise TimeoutError(
            "Owned client was reaped after its deadline; reconcile job identity before replay"
        ) from None
    if len(output.encode()) > 256_000:
        raise ValueError("Client diagnostic budget exceeded")
    return child.returncode, output


def job_artifact() -> Path:
    initialize()
    identity = source_code_identity()
    compiler = subprocess.check_output(
        ["javac", "-version"], stderr=subprocess.STDOUT, text=True
    ).strip()
    if not compiler.startswith("javac 17."):
        raise ValueError("Use the prepared native Java17 compiler")
    descriptor = {"source_files": identity, "compiler": compiler, "flink_version": "2.3.0"}
    artifact_id = hashlib.sha256(json.dumps(descriptor, sort_keys=True).encode()).hexdigest()
    marker = ROOT / "artifacts" / (artifact_id + ".json")
    jar = ROOT / "artifacts" / (artifact_id + ".jar")
    if marker.exists():
        if (
            marker.is_symlink()
            or jar.is_symlink()
            or not jar.is_file()
            or marker.stat().st_size > 32_768
            or jar.stat().st_size > 1_000_000
        ):
            raise ValueError("Invalid retained job artifact")
        old = json.loads(marker.read_text())
        if (
            old.get("descriptor") == descriptor
            and old.get("jar_sha256") == hashlib.sha256(jar.read_bytes()).hexdigest()
        ):
            return jar
        raise ValueError("Retained artifact identity differs; no overwrite performed")
    if jar.exists() or len(list((ROOT / "artifacts").glob("*.jar"))) >= 16:
        raise ValueError("An orphaned artifact or artifact budget needs explicit inspection")
    with tempfile.TemporaryDirectory(prefix="flink-compile-") as temporary:
        target = Path(temporary)
        classes = target / "classes"
        classes.mkdir()
        code, log = process(
            [
                "javac",
                "--release",
                "17",
                "-cp",
                "/opt/flink/lib/*",
                "-d",
                str(classes),
                *[str(p) for p in sorted((SOURCE / "src").glob("*.java"))],
            ],
            60,
        )
        if code:
            raise RuntimeError("Actual Java compilation failed:\n" + log[-5000:])
        packed = target / "jobs.jar"
        code, log = process(
            [
                "jar",
                "--create",
                "--file",
                str(packed),
                "--main-class",
                "WorkshopJobs",
                "-C",
                str(classes),
                ".",
            ],
            30,
        )
        if code:
            raise RuntimeError("Actual JAR packaging failed:\n" + log[-3000:])
        if packed.stat().st_size > 1_000_000:
            raise ValueError("Job artifact exceeds fixture bound")
        with jar.open("xb") as destination:
            destination.write(packed.read_bytes())
    atomic_json(
        marker,
        {"descriptor": descriptor, "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest()},
        replace=marker.exists(),
    )
    return jar


def validate_request(record: dict, action: str) -> None:
    if (
        not isinstance(record, dict)
        or record.get("schema_version") != 1
        or record.get("action") != action
        or action
        not in {
            "check",
            "check-sql",
            "event-time",
            "state",
            "checkpoint",
            "savepoint",
            "backpressure",
        }
        or re.fullmatch(r"[a-f0-9]{32}", str(record.get("request_id", ""))) is None
        or re.fullmatch(r"[a-f0-9]{64}", str(record.get("source_sha256", ""))) is None
        or record.get("output") != "/state/results/" + record["request_id"]
        or record.get("status")
        not in {
            "created",
            "submitting",
            "running",
            "completed",
            "failed",
            "unknown",
            "checkpoint-ready",
            "savepoint-ready",
            "restoring",
        }
    ):
        raise ValueError("Retained request identity/schema differs; no state was changed")
    if (
        record.get("job_id") is not None
        and re.fullmatch(r"[a-f0-9]{32}", str(record["job_id"])) is None
    ):
        raise ValueError("Invalid retained actual job identity")


def archive_request(record: dict) -> None:
    destination = ROOT / "receipts" / (record["request_id"] + "-request.json")
    history = record | {"record_kind": "request-history"}
    if destination.exists():
        if json.loads(destination.read_text()) != history:
            raise ValueError("Prior request history differs; no overwrite performed")
    else:
        atomic_json(destination, history)


def current(action: str) -> tuple[dict, bool]:
    path = ROOT / "requests" / (action + ".json")
    digest = hashlib.sha256(json.dumps(source_code_identity(), sort_keys=True).encode()).hexdigest()
    if path.exists():
        if path.is_symlink() or path.stat().st_size > 100_000:
            raise ValueError("Invalid request record")
        record = json.loads(path.read_text())
        validate_request(record, action)
        if record.get("status") not in {"completed", "failed"}:
            if record.get("source_sha256") != digest:
                raise ValueError(
                    "Source changed during an unfinished request; "
                    "reconcile its retained identity first"
                )
            return record, False
        if record.get("source_sha256") == digest:
            if record["status"] == "failed":
                raise RuntimeError(
                    "Prior failed request is retained; "
                    "inspect readback before an explicit new experiment"
                )
            return record, True
    if path.exists() and record.get("status") == "failed":
        archive_request(record)
    identity = uuid.uuid4().hex
    record = {
        "schema_version": 1,
        "request_id": identity,
        "action": action,
        "source_sha256": digest,
        "status": "created",
        "output": "/state/results/" + identity,
        "job_id": None,
    }
    atomic_json(path, record, replace=path.exists())
    return record, False


def save_request(record: dict) -> None:
    validate_request(record, record.get("action", ""))
    atomic_json(ROOT / "requests" / (record["action"] + ".json"), record, replace=True)


def jobs_named(name: str) -> list[str]:
    return [job["jid"] for job in api("/jobs/overview").get("jobs", []) if job.get("name") == name]


def submit(
    record: dict,
    mode: str,
    *,
    restore: str | None = None,
    parallelism: int = 1,
    detached: bool = True,
) -> str:
    name = "DS60 " + ("sql" if mode == "sql" else mode) + " " + record["request_id"]
    if restore is None and record.get("status") != "created":
        if record.get("job_id"):
            return record["job_id"]
        known = jobs_named(name)
        if len(known) != 1:
            record["status"] = "unknown"
            save_request(record)
            raise RuntimeError("An unfinished submission needs reconciliation; no job was replayed")
        record.update(job_id=known[0], status="running")
        save_request(record)
        return known[0]
    artifact = job_artifact()
    record["artifact"] = str(artifact)
    record["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    args = [FLINK, "run"]
    if detached:
        args.append("-d")
    if restore is not None:
        args.extend(["-s", restore])
    args.extend([str(artifact), mode, record["request_id"], record["output"], str(parallelism)])
    record["status"] = "submitting"
    save_request(record)
    try:
        code, log = process(args, 180)
    except Exception:
        known = jobs_named(name)
        record["status"] = "unknown"
        if len(known) == 1:
            record["job_id"] = known[0]
        save_request(record)
        raise
    (ROOT / "receipts" / (record["request_id"] + "-" + mode + "-client.log")).write_text(log)
    matches = re.findall(r"(?:JobID|Job ID)\s+([a-f0-9]{32})", log)
    known = list(dict.fromkeys(matches)) or jobs_named(name)
    if code or len(known) != 1:
        record.update(status="failed" if code else "unknown", client_exit=code)
        if len(known) == 1:
            record["job_id"] = known[0]
        save_request(record)
        archive_request(record)
        raise RuntimeError(
            "Actual job submission failed or ambiguous; no replay performed:\n" + log[-5000:]
        )
    job = known[0]
    if re.fullmatch(r"[a-f0-9]{32}", job) is None:
        raise ValueError("Unexpected actual job identity")
    record.update(job_id=job, status="running")
    save_request(record)
    return job


def job_state(job: str) -> dict:
    if re.fullmatch(r"[a-f0-9]{32}", job) is None:
        raise ValueError("Invalid owned job identity")
    return api("/jobs/" + job)


def wait_finish(
    record: dict, mode: str, *, restored: bool = False, metrics: list | None = None
) -> dict:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        state = job_state(record["job_id"])
        if state.get("state") == "FINISHED":
            break
        if state.get("state") in TERMINAL:
            record.update(status="failed", actual_job_state=state.get("state"))
            save_request(record)
            raise RuntimeError(
                "Actual job did not finish successfully; inspect its retained ID/logs"
            )
        time.sleep(0.25)
    else:
        raise TimeoutError("Actual job did not finish within its bound; no resubmission performed")
    rows, hashes = result_rows(record["request_id"])
    observation = verify_result(mode, rows)
    checkpoints = {} if mode == "sql" else api("/jobs/" + record["job_id"] + "/checkpoints")
    if restored and not checkpoints.get("latest", {}).get("restored"):
        raise ValueError("No actual restored checkpoint is reported")
    receipt = {
        **record,
        "status": "completed",
        "passed": True,
        "actual_flink": True,
        "mode": mode,
        "observation": observation,
        "result_sha256": hashes,
        "checkpoint_summary": checkpoints.get("counts", {}),
        "restored_checkpoint": checkpoints.get("latest", {}).get("restored"),
        "metrics": metrics or [],
    }
    if record.get("savepoint"):
        receipt["savepoint"] = record["savepoint"]
    if record.get("incompatible_restore_rejected"):
        receipt["incompatible_restore_rejected"] = True
    destination = ROOT / "receipts" / (record["request_id"] + ".json")
    try:
        if destination.exists():
            if json.loads(destination.read_text()) != receipt:
                raise ValueError("Retained receipt differs; no replacement performed")
        else:
            atomic_json(destination, receipt)
        record.update(status="completed", receipt=str(destination))
        save_request(record)
    except OSError as error:
        return receipt | {
            "storage_warning": "Actual completed result is shown; receipt/pointer save failed: "
            + type(error).__name__
        }
    return receipt


def saved(record: dict) -> dict:
    path = Path(record["receipt"])
    if (
        path.parent != ROOT / "receipts"
        or path.name != record["request_id"] + ".json"
        or path.is_symlink()
        or path.stat().st_size > 100_000
    ):
        raise ValueError("Invalid saved receipt")
    receipt = json.loads(path.read_text())
    if (
        not isinstance(receipt, dict)
        or any(
            receipt.get(key) != record.get(key)
            for key in ("schema_version", "request_id", "action", "source_sha256", "job_id")
        )
        or receipt.get("passed") is not True
        or receipt.get("actual_flink") is not True
        or receipt.get("status") != "completed"
    ):
        raise ValueError("Saved receipt differs from the retained request identity")
    return receipt | {"saved_readback_no_execution": True}


def wait_checkpoint(record: dict) -> dict:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = job_state(record["job_id"])
        checkpoints = api("/jobs/" + record["job_id"] + "/checkpoints")
        if (
            state.get("state") == "RUNNING"
            and checkpoints.get("counts", {}).get("completed", 0) > 0
            and Path(record["output"]).is_dir()
        ):
            rows, _ = result_rows(record["request_id"])
            if rows:
                return checkpoints | {"observed_finished_rows": len(rows)}
        if state.get("state") in TERMINAL:
            raise RuntimeError(
                "Recovery observation window was missed before the deliberate interruption"
            )
        time.sleep(0.2)
    raise TimeoutError("No actual completed checkpoint appeared")


def check(action: str, mode: str) -> dict:
    record, cached = current(action)
    if cached:
        return saved(record)
    submit(record, mode, detached=mode != "sql")
    return wait_finish(record, mode)


def checkpoint_begin() -> dict:
    record, cached = current("checkpoint")
    if cached:
        return saved(record)
    submit(record, "checkpointed")
    stats = wait_checkpoint(record)
    record.update(
        status="checkpoint-ready",
        completed_before_interruption=stats.get("counts", {}).get("completed"),
        finished_rows_before_interruption=stats["observed_finished_rows"],
    )
    save_request(record)
    return {
        "checkpoint_ready": True,
        "job_id": record["job_id"],
        "completed": record["completed_before_interruption"],
        "finished_rows_before_interruption": record["finished_rows_before_interruption"],
    }


def savepoint() -> dict:
    record, cached = current("savepoint")
    if cached:
        return saved(record)
    if record.get("status") not in {"created", "submitting", "running"}:
        raise RuntimeError(
            "A partially completed savepoint experiment needs inspection; "
            "it is not automatically replayed"
        )
    submit(record, "checkpointed")
    wait_checkpoint(record)
    code, log = process([FLINK, "stop", "-p", "file:///state/savepoints", record["job_id"]], 120)
    (ROOT / "receipts" / (record["request_id"] + "-stop.log")).write_text(log)
    paths = re.findall(r"(?:file:)?(/state/savepoints/savepoint-[A-Za-z0-9_-]+)", log)
    if code or not paths:
        raise RuntimeError("Actual stop/savepoint did not confirm an owned path:\n" + log[-4000:])
    point = Path(paths[-1])
    if point.parent != ROOT / "savepoints" or point.is_symlink() or not point.is_dir():
        raise ValueError("Returned savepoint is outside owned state")
    record.update(
        status="savepoint-ready", savepoint="file://" + str(point), stopped_job_id=record["job_id"]
    )
    save_request(record)
    before = {
        str(p.relative_to(ROOT / "results")): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in Path(record["output"]).rglob("*")
        if p.is_file()
    }
    args = [
        FLINK,
        "run",
        "-s",
        record["savepoint"],
        str(job_artifact()),
        "changed-uid",
        record["request_id"],
        record["output"],
        "1",
    ]
    code, log = process(args, 120)
    (ROOT / "receipts" / (record["request_id"] + "-incompatible.log")).write_text(log)
    text = log.lower()
    mapping_errors = (
        "cannot map checkpoint/savepoint state",
        "can not map checkpoint/savepoint state",
        "no operator for the state",
        "non-restored state",
    )
    if code == 0 or not any(marker in text for marker in mapping_errors):
        raise ValueError(
            "The negative restore did not demonstrate the intended operator/state mapping rejection"
        )
    after = {
        str(p.relative_to(ROOT / "results")): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in Path(record["output"]).rglob("*")
        if p.is_file()
    }
    if after != before:
        raise ValueError("Negative restore changed retained output")
    record.update(incompatible_restore_rejected=True, status="restoring")
    save_request(record)
    submit(record, "checkpointed", restore=record["savepoint"], parallelism=2)
    return wait_finish(record, "checkpointed", restored=True)


def accumulated_pressure(state: dict) -> list[dict]:
    observed = []
    for vertex in state.get("vertices", []):
        if "pressure-payload-producer" not in vertex.get("name", ""):
            continue
        value = vertex.get("metrics", {}).get("accumulated-backpressured-time")
        if value is not None and math.isfinite(float(value)):
            observed.append(
                {
                    "id": "accumulated-backpressured-time",
                    "value": str(value),
                    "units": "milliseconds",
                    "vertex": vertex["name"],
                    "source": "actual-task-rest-metrics",
                }
            )
    return observed


def pressure() -> dict:
    record, cached = current("backpressure")
    if cached:
        return saved(record)
    submit(record, "pressure")
    observations = []
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        state = job_state(record["job_id"])
        observations.extend(accumulated_pressure(state))
        for vertex in state.get("vertices", []):
            if "pressure-payload-producer" not in vertex.get("name", ""):
                continue
            vertex_id = vertex["id"]
            if re.fullmatch(r"[a-f0-9]{32}", vertex_id) is None:
                raise ValueError("Invalid actual vertex identity")
            base = "/jobs/" + record["job_id"] + "/vertices/" + vertex_id + "/subtasks/0/metrics"
            available = api(base)
            ids = [
                item["id"]
                for item in available
                if "backPressuredTimeMsPerSecond" in item.get("id", "")
            ]
            if any(re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", name) is None for name in ids):
                raise ValueError("Unexpected metric identifier")
            if ids:
                values = api(base + "?get=" + urllib.parse.quote(",".join(ids), safe=","))
                observations.extend(values)
        if state.get("state") in TERMINAL:
            break
        time.sleep(0.3)
    measured = [float(row["value"]) for row in observations if math.isfinite(float(row["value"]))]
    if not measured or max(measured) <= 0:
        raise ValueError("Configured delay did not produce an actual positive backpressure metric")
    return wait_finish(record, "pressure", metrics=observations)


def readback() -> dict:
    values = []
    paths = sorted((ROOT / "receipts").glob("*.json"))
    if len(paths) > 32 or any(p.is_symlink() or p.stat().st_size > 100_000 for p in paths):
        raise ValueError("Saved receipt budget exceeded")
    for path in paths:
        values.append(json.loads(path.read_text()))
    requests = sorted((ROOT / "requests").glob("*.json"))
    if len(requests) > 16 or any(
        path.is_symlink() or path.stat().st_size > 100_000 for path in requests
    ):
        raise ValueError("Request count/size exceeds fixed-action contract")
    return {
        "receipts": values,
        "requests": [json.loads(p.read_text()) for p in requests],
        "read_only_no_submission": True,
    }


def reconcile() -> dict:
    observations = []
    modes = {
        "check": "bounded",
        "check-sql": "sql",
        "event-time": "windows",
        "state": "state",
        "backpressure": "pressure",
    }
    for path in sorted((ROOT / "requests").glob("*.json")):
        record = json.loads(path.read_text())
        action = path.stem
        validate_request(record, action)
        if record["status"] in {"completed", "failed"}:
            continue
        if action == "checkpoint" and record.get("job_id"):
            state = job_state(record["job_id"])
            stats = api("/jobs/" + record["job_id"] + "/checkpoints")
            if state.get("state") == "FINISHED" and not stats.get("latest", {}).get("restored"):
                record.update(
                    status="failed",
                    actual_job_state="FINISHED",
                    recovery_experiment="finished_without_required_interruption",
                )
                save_request(record)
                archive_request(record)
                observations.append(
                    {
                        "action": action,
                        "passed": False,
                        "recovery_demonstrated": False,
                        "no_submission_performed": True,
                    }
                )
                continue
        if action not in modes or not record.get("job_id"):
            observations.append(
                {"action": action, "status": record["status"], "manual_state_review_required": True}
            )
            continue
        state = job_state(record["job_id"])
        if state.get("state") == "FINISHED":
            measured = accumulated_pressure(state) if action == "backpressure" else []
            if action == "backpressure" and not any(float(row["value"]) > 0 for row in measured):
                raise ValueError("No actual accumulated backpressure was observed")
            observations.append(wait_finish(record, modes[action], metrics=measured))
        else:
            observations.append(
                {
                    "action": action,
                    "job_id": record["job_id"],
                    "actual_job_state": state.get("state"),
                    "no_submission_performed": True,
                }
            )
    return {"reconciled": observations, "no_submission_performed": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "health-jm",
            "health-tm",
            "ready",
            "check",
            "check-sql",
            "event-time",
            "state",
            "checkpoint-begin",
            "checkpoint-restart-needed",
            "checkpoint-finish",
            "savepoint",
            "backpressure",
            "readback",
            "reconcile",
        ],
    )
    action = parser.parse_args().action
    if action in {"health-jm", "health-tm", "ready"}:
        result = health(action != "health-jm")
    elif action == "readback":
        result = readback()
    elif action == "reconcile":
        result = reconcile()
    elif action == "checkpoint-begin":
        result = checkpoint_begin()
    elif action == "checkpoint-restart-needed":
        record, cached = current("checkpoint")
        return 1 if cached else 0 if record.get("status") == "checkpoint-ready" else 2
    elif action == "checkpoint-finish":
        record, cached = current("checkpoint")
        result = saved(record) if cached else wait_finish(record, "checkpointed", restored=True)
    elif action == "savepoint":
        result = savepoint()
    elif action == "backpressure":
        result = pressure()
    else:
        result = check(
            action,
            {"check": "bounded", "check-sql": "sql", "event-time": "windows", "state": "state"}[
                action
            ],
        )
    print(json.dumps(result, indent=2, allow_nan=False))
    return 1 if "storage_warning" in result else 0


if __name__ == "__main__":
    raise SystemExit(main())
