# apache-083: Orchestrated backfills and live data

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-032`, `apache-050`, `apache-081`.

## Key terms

- **Logical interval:** The Airflow data interval a run is responsible for, distinct from the task's wall-clock start time.
- **Event-time clock:** The timestamps and watermarks a stream processor uses to decide which records belong to a window.
- **Output ownership:** The rule naming which writer, backfill or live stream, owns each published partition, so one cannot silently overwrite the other.
- **Cutover policy:** The explicit boundary at which responsibility for a date range passes from the batch backfill to the live stream.

## Orchestration intervals and event time describe different clocks

Airflow schedules and tracks workflow runs over defined logical intervals. A
stream processor reasons about event timestamps, watermarks and continuously
arriving records. A historical backfill and a live stream can therefore operate
on overlapping business dates while following different execution clocks.
Naming both a daily job does not make their boundaries equivalent.

The actual Airflow workshop teaches explicit interval behavior and idempotent
publication. Kafka/Flink examples teach retained positions and event-time state.
Combining them requires an explicit output ownership and cutover policy. A
backfill must not silently overwrite the live producer's current output or
consume its state as though both writers were one atomic operation.

Use half-open intervals such as \([a,b)\) when defining a batch's intended
coverage, and state timezone and timestamp unit. Events exactly at a boundary
must belong to one selected interval. Wall-clock task start, logical data interval
and the latest event timestamp are different fields in a reproducible receipt.

## Worked case A: correct one historical partition

Choose a known historical UTC day and a bounded three-order input snapshot.
Trigger the actual owned Airflow workflow with the intended interval and source
identity. Write its candidate output to a separate owned location, compare exact
IDs and regional totals, then use an explicit publication step for that day.
Keep the previous accepted output recoverable until the new result is verified.

A retry should reconcile a known candidate or published identity rather than
blindly appending the same batch again. Capture workflow/run/task identity,
source revision, logical interval, attempt and output identity. A task can fail
after publishing its output but before saving a receipt, so a failed status alone
is not proof that no external effect occurred.

The course's actual Airflow timetable correction demonstrates why interval
readback matters: a shorthand schedule assumption can differ from the intended
coverage. Always inspect the actual selected interval in the running release.
Do not manufacture an expected date range from the trigger timestamp after the
workflow has already produced data.

## Worked case B: keep the live path independently owned

While the historical correction is prepared, the live path continues to consume
new events under its own source positions and state. Use separate candidate
outputs or an explicit table commit protocol so the backfill does not reset
consumer offsets, checkpoint directories or serving segments. Record which writer
owns each publication boundary.

A late event for the corrected day can arrive after backfill acceptance. Decide
whether it creates a later correction, enters a late-data queue or is excluded
by a closed-period policy. That is a business completeness decision, not something
Airflow's schedule or Flink's watermark can determine universally.

If a serving table combines historical and fresh data, define the actual time
boundary and verify no gap or overlap around the cutover. Test an event exactly
at the boundary and a delayed correction. Equal aggregate totals can hide a
missing event canceled by a duplicate, so keep identity-level reconciliation.

## Diagnosis and interview discussion

Compare logical interval, input snapshot, event timestamps, writer ownership,
publication identity and live source positions. Distinguish task retry from event
replay and distinguish both from an intentional correction. Preserve unknown
publication outcomes for read-only reconciliation instead of immediately rerunning
a writer.

**Interview discussion: why is a backfill not simply restarting the live stream
from yesterday?** It can use different bounded inputs, publication rules and
business correction semantics, while the live stream retains independent state.
These cases correct one historical partition and keep continuous processing
separate until an explicit reconciled cutover joins their outputs.

## Worked examples

### Map an interval to the partition it rewrites

```python
from datetime import datetime, timedelta, timezone

start = datetime(2026, 1, 1, tzinfo=timezone.utc)
end = start + timedelta(days=1)
partition = start.date().isoformat()
print(partition, start.isoformat(), end.isoformat())
```

```text
2026-01-01 2026-01-01T00:00:00+00:00 2026-01-02T00:00:00+00:00
```

Airflow passes data_interval_start and data_interval_end to a run; the job should derive the partition from those, not from the wall clock. Then rerunning the 2026-01-01 interval next week still rewrites only that day. Event time inside the rows is a third clock: late events from that day can arrive after the interval ran, which is why correction runs exist at all.

### Rerun one historical interval

```bash
cd work/airflow
bash run.sh backfill-check
bash run.sh readback
```

The backfill route triggers runs for explicit past intervals and the readback shows which outputs each produced. Publish the corrected partition as a candidate, validate it against an independent count, and only then swap it in. The live streaming path keeps writing current data meanwhile, so the backfill must never touch today's partition or it will race the stream.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-083 complete worked notebook

Use the actual Airflow project for one explicit historical interval. Publish a validated candidate separately from the live stream. Reconcile unknown publication outcomes before retrying any writer.

## What this backfill receipt must hold

- The DAG ID, run ID, logical date and the half-open data interval Airflow selected.
- Each task attempt number, with the identified fail-once retry kept separate.
- The input snapshot or file version the task read, as recorded in its own receipt.
- The candidate output location and its identity before publication.
- The published output identity, and the untouched identity of the other day.
- The live stream's source positions at the moment of cutover.

The Airflow workshop gives a concrete oracle. Day one holds amounts 4 and 9 and
day two holds 7. The correction changes 4 to 6, so day one becomes 15 while day
two stays byte-for-byte equal. If day two's identity changes, the backfill wrote
outside its interval. If the run ID is new but the published identity is
unchanged, check whether the earlier attempt had already published. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../airflow/README.md
cat ../airflow/dags/classroom_workflows.py
```

In `classroom_workflows.py`, find the `classroom_orders` DAG: its
`CronDataIntervalTimetable` and its start and end dates explain why only two UTC
days exist. Then find `classroom_correction`, whose `correct` task writes only the
first day and raises for any other. Reading the DAG shows intent. Only `run.sh backfill-check` and `run.sh readback` against
the running workshop show the interval and outputs that Airflow actually produced.

## Primary references

- [Airflow backfill of historical intervals](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/backfill.html)
- [Airflow Dag Run data intervals](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/dag-run.html)
- [Flink event time for the live path](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/event-time/generating_watermarks/)
