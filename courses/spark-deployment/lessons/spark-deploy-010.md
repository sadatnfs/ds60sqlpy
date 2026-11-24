# spark-deploy-010: Retain event logs and read completed history

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-009`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Preserve events before the driver exits

Event logging must be enabled before the application starts. A History Server reads those persisted events and reconstructs application views. It does not replay the computation. A driver log is text from that process; a Spark event log is structured application history. Keep them distinct when diagnosing a failure.

This Compose lab mounts the same owned event directory writable in the driver and read-only in History Server. That works on one host. The path `file:/events` would refer to different disks on different machines unless a real shared storage mount exists. Cloud/object-store paths require matching filesystem connectors, credentials and storage semantics.

## Key terms

- **Event log:** Structured application history the driver writes when event logging is enabled before startup.
- **History Server:** A service that reads persisted event logs and reconstructs application views without replaying computation.
- **Driver log:** Plain text output from the driver process, distinct from the structured event log.
- **Shared event directory:** Storage mounted writable in the driver and read-only in the History Server, valid across machines only with real shared storage.
- **Retention policy:** The configured compaction, cleaning and storage budget that decide how long application history remains readable.

## Worked case A: read a completed application

```sh
python3 lab.py submit
python3 lab.py urls
```

Event logging is switched on for every application by the shared defaults:

From [`projects/cluster-lab/conf/spark-defaults.conf`](../projects/cluster-lab/conf/spark-defaults.conf):

```properties
spark.eventLog.enabled               true
spark.eventLog.dir                   file:/events
```

`/events` is a mounted directory in the workshop state, so the history server can
read the log after the driver container has gone.

Open the History Server URL, find the exact application ID from the bounded JSON result and inspect its completed stages. Allow its configured scan interval to observe finalized events; the absence of a new listing immediately after submission does not establish data loss. Keep the result receipt, event filenames and source identity together.

```text
driver setting: spark.eventLog.enabled=true
driver location: spark.eventLog.dir=file:/events
history location: spark.history.fs.logDirectory=file:/events
history cleaner: disabled for this owned teaching fixture
```

The expected observation is historical application readback after `spark.stop()`. The source-only qualification record must remain not-run until this actual readback is observed.

## Worked case B: replace containers and retain history

```sh
python3 lab.py down
python3 lab.py up
```

No application is submitted by these commands. Inspect the same application ID and compare its event files' hashes with the recorded pre-replacement values. If the History Server shows that application without a new run, the observation supports retained-event readback. New container IDs are compatible with retained history. Do not create a fresh successful application to conceal a missing old one.

## Worked example: comparing the driver write path with the history read path

```python
import shlex

defaults = """
spark.eventLog.enabled true
spark.eventLog.dir file:/events
"""
history_opts = (
    "-Dspark.history.fs.logDirectory=file:/events -Dspark.history.fs.cleaner.enabled=false"
)

driver = dict(line.split(None, 1) for line in defaults.strip().splitlines())
history = dict(token[2:].split("=", 1) for token in shlex.split(history_opts))
print(
    "driver writes to ", driver["spark.eventLog.dir"], "enabled:", driver["spark.eventLog.enabled"]
)
print("history reads from", history["spark.history.fs.logDirectory"])
print("paths agree:", driver["spark.eventLog.dir"] == history["spark.history.fs.logDirectory"])
print("cleaner:", history["spark.history.fs.cleaner.enabled"])
moved = history_opts.replace("file:/events", "file:/tmp/events")
history = dict(token[2:].split("=", 1) for token in shlex.split(moved))
print(
    "after a careless edit, paths agree:",
    driver["spark.eventLog.dir"] == history["spark.history.fs.logDirectory"],
)
```

Output from running the block above:

```text
driver writes to  file:/events enabled: true
history reads from file:/events
paths agree: True
cleaner: false
after a careless edit, paths agree: False
```

The History Server in this lab receives its settings through `SPARK_HISTORY_OPTS` in `entrypoint.py`, while the driver reads `spark.eventLog.dir` from `spark-defaults.conf`. They live in different files, so nothing forces them to agree. The script parses both exactly as written in the project and confirms that the driver writes to `file:/events` and the server reads from `file:/events`, with the cleaner disabled so retained logs are not pruned during an evidence test. The last line simulates a one-word edit to the history options; the paths no longer match and the History Server would show an empty listing while every application still completes normally. That is the first comparison the chapter recommends when the history page is empty, before permissions or format versions. Remember that agreeing strings are still only half of the story on multiple hosts, where `file:/events` names a different disk on each machine unless a real shared mount backs it.

## Worked example: telling a finished event log from an interrupted one

```python
import json

logs = {
    "app-20260115101500-0004": [
        {
            "Event": "SparkListenerApplicationStart",
            "App ID": "app-20260115101500-0004",
            "Timestamp": 1768471500000,
        },
        {"Event": "SparkListenerJobEnd", "Job ID": 0, "Job Result": {"Result": "JobSucceeded"}},
        {"Event": "SparkListenerApplicationEnd", "Timestamp": 1768471563000},
    ],
    "app-20260115102000-0005.inprogress": [
        {
            "Event": "SparkListenerApplicationStart",
            "App ID": "app-20260115102000-0005",
            "Timestamp": 1768471800000,
        },
        {"Event": "SparkListenerJobStart", "Job ID": 0},
    ],
}
for name, events in logs.items():
    lines = "\n".join(json.dumps(e) for e in events)
    kinds = [json.loads(line)["Event"] for line in lines.splitlines()]
    finished = "SparkListenerApplicationEnd" in kinds
    print(
        f"{name}: {len(kinds)} events, finished={finished}, suffix={name.endswith('.inprogress')}"
    )
    if finished:
        start = events[0]["Timestamp"]
        print(f"  duration {(events[-1]['Timestamp'] - start) / 1000:.0f}s")
```

Output from running the block above:

```text
app-20260115101500-0004: 3 events, finished=True, suffix=False
  duration 63s
app-20260115102000-0005.inprogress: 2 events, finished=False, suffix=True
```

Spark writes event logs as newline-delimited JSON, and an application still running, or one whose driver died, keeps the `.inprogress` suffix and lacks a `SparkListenerApplicationEnd` record. The two stand-in logs are minimal fabrications that follow that format, not files captured from the lab. The completed one has three events and a 63 second span between start and end timestamps; the interrupted one stops after a job start and still carries the suffix. The History Server lists both, but only the first supports a claim that the application finished. During the container replacement in Worked case B, a log that remains `.inprogress` after `lab.py down` means the driver was stopped before `spark.stop()` flushed its end event, and the right response is to preserve that file for diagnosis rather than resubmit. Rolling or compressed logs need their own reader, so check `spark.eventLog.rolling.enabled` and the codec before applying a simple parser like this.

## Diagnose and transfer

If the history page is empty, first compare effective log paths and mounts. Then inspect file permissions and format/version compatibility, including compressed or rolling event logs. An uncleanly terminated driver may leave an incomplete log; preserve it for diagnosis. History Server compaction and cleaning change retention and must be deliberately configured, not introduced during an evidence-preservation test.

Event logs can be much larger than the final numerical result. Set retention, storage budgets and access policies for long-lived deployments. Do not place secrets in Spark configuration and assume the event stream will hide them. Completed task history also does not establish that an external sink transaction committed; inspect that sink's own publication receipt.

## Primary references

- [Spark event logs and History Server](https://spark.apache.org/docs/4.0.1/monitoring.html)
- [Event-log security](https://spark.apache.org/docs/4.0.1/security.html#event-logging)
