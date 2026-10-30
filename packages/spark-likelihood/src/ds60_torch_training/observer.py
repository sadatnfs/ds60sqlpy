# SPDX-License-Identifier: Apache-2.0
"""Independent, bounded Spark listener evidence for executor training.

The existing prepared integration Probe supplies JVM observations. Python rank
claims alone do not establish executor placement. No Spark/Torch import occurs
at module import, and this observer never builds or downloads the probe.
"""

from __future__ import annotations

import json
import time
import weakref
from pathlib import Path
from typing import Protocol
from urllib.parse import unquote, urlparse

from .contracts import (
    TrainingError,
    canonical_json,
    digest,
    integer,
    read_json,
    require_sha,
    sha256_file,
)

MAX_EVENTS = 10000
MAX_OBSERVATION_BYTES = 1_000_000
_ATTACHED = weakref.WeakKeyDictionary()


class ExecutorObserver(Protocol):
    def before(self, spark, plan: dict) -> dict: ...
    def after(
        self,
        spark,
        plan: dict,
        token: dict,
        result: dict | None,
        *,
        error: dict | None = None,
    ) -> dict: ...


def _list(raw: str, name: str) -> list[dict]:
    if type(raw) is not str or len(raw.encode()) > MAX_OBSERVATION_BYTES:
        raise TrainingError(name + " exceeds the observation bound")
    try:
        value = json.loads(raw)
    except (ValueError, TypeError, RecursionError) as error:
        raise TrainingError("Malformed " + name) from error
    if (
        type(value) is not list
        or len(value) > MAX_EVENTS
        or any(type(row) is not dict for row in value)
    ):
        raise TrainingError("Invalid bounded " + name)
    canonical_json(value, limit=MAX_OBSERVATION_BYTES)
    return value


def _probe_identity(jvm, jar: Path, manifest_path: Path, source: Path) -> dict:
    metadata = read_json(manifest_path)
    if metadata.get("schema_version") != 1 or metadata.get("scope") != "compilation only":
        raise TrainingError("Require the existing compiled integration Probe metadata")
    source_sha = sha256_file(source, max_bytes=1_000_000)
    jar_sha = sha256_file(jar, max_bytes=8_000_000)
    if metadata.get("source_sha256") != source_sha or metadata.get("jar_sha256") != jar_sha:
        raise TrainingError("Prepared probe source/JAR identity mismatch")
    loader = jvm.java.lang.Thread.currentThread().getContextClassLoader()
    cls = jvm.java.lang.Class.forName("io.ds60.integration.Probe$", True, loader)
    location = str(cls.getProtectionDomain().getCodeSource().getLocation().toString())
    parsed = urlparse(location)
    if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
        raise TrainingError("Loaded probe must have an inspectable local JAR")
    loaded = Path(unquote(parsed.path))
    if sha256_file(loaded, max_bytes=8_000_000) != jar_sha:
        raise TrainingError("Loaded integration Probe differs from prepared JAR")
    return {
        "source_sha256": source_sha,
        "jar_sha256": jar_sha,
        "loaded_jar_sha256": jar_sha,
        "metadata_sha256": sha256_file(manifest_path, max_bytes=1_000_000),
    }


class ProbeObserver:
    """Use the already prepared Probe, with no two-task probe in single mode.

    already_attached is only for a caller whose existing integration controller
    attached this exact Probe listener. Subsequent uses on the same context are
    tracked without adding duplicate listeners. Application ownership stays with
    the caller; this class never stops Spark.
    """

    def __init__(
        self,
        *,
        probe_jar: Path | str,
        probe_manifest: Path | str,
        probe_source: Path | str,
        already_attached: bool = False,
    ):
        if type(already_attached) is not bool:
            raise TrainingError("already_attached must be an explicit bool")
        self.jar, self.manifest, self.source = map(Path, (probe_jar, probe_manifest, probe_source))
        self.already_attached = already_attached

    def before(self, spark, plan: dict) -> dict:
        context = spark.sparkContext
        identity = _probe_identity(context._jvm, self.jar, self.manifest, self.source)
        probe = context._jvm.io.ds60.integration.Probe
        previous = _ATTACHED.get(context)
        if previous is not None and previous != identity:
            raise TrainingError("This context already has a different admitted Probe")
        if previous is None:
            if not self.already_attached:
                probe.attach(spark._jsparkSession)
            _ATTACHED[context] = identity
        baseline = _list(str(probe.eventsJson()), "listener events")
        identities = []
        if plan["world_size"] == 2:
            identities = _list(str(probe.identities(spark._jsparkSession)), "before identities")
        return {
            "kind": "ds60-torch-probe-token",
            "run_id": plan["run_id"],
            "baseline_events": len(baseline),
            "before_identities": identities,
            "probe_identity": identity,
        }

    def after(
        self,
        spark,
        plan: dict,
        token: dict,
        result: dict | None,
        *,
        error: dict | None = None,
    ) -> dict:
        if token.get("kind") != "ds60-torch-probe-token" or token.get("run_id") != plan["run_id"]:
            raise TrainingError("Observation token belongs to another run")
        probe = spark.sparkContext._jvm.io.ds60.integration.Probe
        after = []
        if error is None and plan["world_size"] == 2:
            after = _list(str(probe.identities(spark._jsparkSession)), "after identities")
        excluded = sorted({row["stage_id"] for row in token["before_identities"] + after})
        # Listener delivery is asynchronous. Give the last completed tasks a short
        # bounded drain window. No new probe is scheduled after a failed run.
        until = time.monotonic() + min(2.0, float(plan["timeout_seconds"]))
        while True:
            events = _list(str(probe.eventsJson()), "listener events")
            if len(events) < token["baseline_events"]:
                raise TrainingError("Listener history was reset during training")
            selected = events[token["baseline_events"] :]
            ended = [
                row
                for row in selected
                if row.get("kind") == "task_end" and row.get("stage_id") not in excluded
            ]
            if error is not None or len(ended) >= plan["world_size"] or time.monotonic() >= until:
                break
            time.sleep(0.02)
        observation = {
            "schema_version": 1,
            "kind": "ds60-torch-executor-observation",
            "run_id": plan["run_id"],
            "probe_identity": token["probe_identity"],
            "before_identities": token["before_identities"],
            "after_identities": after,
            "excluded_stage_ids": excluded,
            "events": selected,
        }
        canonical_json(observation, limit=MAX_OBSERVATION_BYTES)
        return observation


def _identities(value, world: int) -> dict:
    if type(value) is not list or len(value) != world:
        raise TrainingError("Incomplete independent executor identity probe")
    result = {}
    partitions = set()
    for row in value:
        if type(row) is not dict or row.get("kind") != "executor_identity":
            raise TrainingError("Invalid executor identity record")
        executor = row.get("executor_id")
        if type(executor) is not str or not executor or executor == "driver" or executor in result:
            raise TrainingError("Identity probe lacks distinct non-driver executors")
        integer(row.get("pid"), "executor JVM pid", 1)
        integer(row.get("stage_id"), "probe stage", 0)
        integer(row.get("partition_id"), "probe partition", 0, world - 1)
        integer(row.get("attempt"), "probe attempt", 0, 0)
        integer(row.get("stage_attempt"), "probe stage attempt", 0, 0)
        if type(row.get("host")) is not str or not row["host"]:
            raise TrainingError("Missing independent executor hostname")
        partitions.add(row["partition_id"])
        result[executor] = row
    if partitions != set(range(world)):
        raise TrainingError("Identity probe partition coverage differs")
    return result


def validate_evidence(plan: dict, result: dict, observation: dict) -> dict:
    """Validate raw listener/rank records rather than a caller's success flag."""
    canonical_json(observation, limit=MAX_OBSERVATION_BYTES)
    required = {
        "schema_version",
        "kind",
        "run_id",
        "probe_identity",
        "before_identities",
        "after_identities",
        "excluded_stage_ids",
        "events",
    }
    if (
        type(observation) is not dict
        or set(observation) != required
        or type(observation["schema_version"]) is not int
        or observation["schema_version"] != 1
        or observation["kind"] != "ds60-torch-executor-observation"
        or observation["run_id"] != plan["run_id"]
    ):
        raise TrainingError("Malformed independent observation")
    identity = observation["probe_identity"]
    if type(identity) is not dict or set(identity) != {
        "source_sha256",
        "jar_sha256",
        "loaded_jar_sha256",
        "metadata_sha256",
    }:
        raise TrainingError("Missing independent probe source identity")
    for value in identity.values():
        require_sha(value, "probe identity")
    if identity["jar_sha256"] != identity["loaded_jar_sha256"]:
        raise TrainingError("Loaded probe identity mismatch")
    world = plan["world_size"]
    before = after = {}
    if world == 2:
        before = _identities(observation["before_identities"], world)
        after = _identities(observation["after_identities"], world)
        if set(before) != set(after) or any(
            (before[key]["host"], before[key]["pid"]) != (after[key]["host"], after[key]["pid"])
            for key in before
        ):
            raise TrainingError("Executor identities changed within a completed attempt")
    elif observation["before_identities"] or observation["after_identities"]:
        raise TrainingError("Single mode must not require the two-task identity probe")
    expected_excluded = sorted(
        {
            row["stage_id"]
            for row in observation["before_identities"] + observation["after_identities"]
        }
    )
    if observation["excluded_stage_ids"] != expected_excluded:
        raise TrainingError("Unproven stages cannot be excluded from training evidence")
    events = observation["events"]
    if (
        type(events) is not list
        or len(events) > MAX_EVENTS
        or any(type(row) is not dict for row in events)
    ):
        raise TrainingError("Invalid bounded listener events")
    if any(row.get("kind") == "executor_removed" for row in events):
        raise TrainingError("Executor removal cannot be accepted as a completed attempt")
    tasks = [
        row
        for row in events
        if row.get("kind") in {"task_start", "task_end"}
        and row.get("stage_id") not in expected_excluded
    ]
    starts = [row for row in tasks if row["kind"] == "task_start"]
    ends = [row for row in tasks if row["kind"] == "task_end"]
    if len(starts) != world or len(ends) != world:
        raise TrainingError("Missing, duplicate or retried training tasks")
    if len({row.get("stage_id") for row in tasks}) != 1:
        raise TrainingError("Expected one isolated public-run barrier stage")
    start_by_id = {}
    for row in tasks:
        integer(row.get("stage_id"), "stage ID", 0)
        integer(row.get("stage_attempt"), "stage attempt", 0, 0)
        integer(row.get("attempt"), "task attempt", 0, 0)
        integer(row.get("partition_id"), "barrier partition", 0, world - 1)
        integer(row.get("task_id"), "task ID", 0)
        if (
            type(row.get("executor_id")) is not str
            or not row["executor_id"]
            or row["executor_id"] == "driver"
        ):
            raise TrainingError("Training task is not on an identified executor")
        if type(row.get("host")) is not str or not row["host"]:
            raise TrainingError("Training task lacks a host")
        if row["kind"] == "task_start":
            if row["task_id"] in start_by_id:
                raise TrainingError("Duplicate task-start identity")
            start_by_id[row["task_id"]] = row
    receipts = result["rank_receipts"]
    if {row["partition_id"] for row in ends} != set(range(world)) or len(
        {row["executor_id"] for row in ends}
    ) != world:
        raise TrainingError("Incomplete rank coverage or non-distinct executor placement")
    matched = []
    for end in sorted(ends, key=lambda row: row["partition_id"]):
        if end.get("successful") is not True:
            raise TrainingError("A failed task cannot attest training completion")
        start = start_by_id.get(end["task_id"])
        if start is None or any(
            start[key] != end[key]
            for key in (
                "stage_id",
                "stage_attempt",
                "partition_id",
                "task_id",
                "attempt",
                "executor_id",
                "host",
            )
        ):
            raise TrainingError("Task start/end identities disagree")
        rank = end["partition_id"]
        receipt = receipts[rank]
        if receipt["rank"] != rank or receipt["world_size"] != world:
            raise TrainingError("Rank receipt differs from independent partition mapping")
        hosts = {receipt["hostname"], *receipt["host_addresses"]}
        if end["host"] not in hosts:
            raise TrainingError("Rank hostname/IP differs from listener placement")
        if world == 2:
            external = before.get(end["executor_id"])
            if external is None or external["host"] not in hosts:
                raise TrainingError("Training executor differs from independent probe")
        matched.append(
            {
                "rank": rank,
                "executor_id": end["executor_id"],
                "host": end["host"],
                "stage_id": end["stage_id"],
                "task_id": end["task_id"],
                "rank_pid": receipt["pid"],
                "jvm_pid": before[end["executor_id"]]["pid"] if world == 2 else None,
            }
        )
    return {
        "kind": "ds60-torch-verified-executor-evidence",
        "run_id": plan["run_id"],
        "world_size": world,
        "matched_ranks": matched,
        "probe_identity": identity,
        "observation_digest": digest(observation),
        "physical_host_count": "not_attested_by_listener",
    }
