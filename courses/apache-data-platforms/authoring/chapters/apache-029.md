## Backfill changes scheduling coverage, not the meaning of time

A schedule defines eligible intervals. Catchup determines whether historical
scheduled intervals are created when a DAG becomes active, while a backfill
operation explicitly requests a historical range under its own run controls.
Neither automatically guarantees that a data source was complete, that a sink
was idempotent or that a correction reached every downstream consumer.

The workshop's daily DAG has only two historical intervals, starts paused and
uses bounded concurrency. This finite design prevents a learner from accidentally
creating months of catchup work. The resulting metadata still shows real scheduled
runs and their intervals. A separate manually triggered correction DAG receives
one validated day, making its scope visible rather than overloading a wall-clock
execution timestamp.

A partitioned data product should define which version is current, how a correction
is recorded and whether downstream systems refresh automatically. Rewriting one
partition while leaving its source identity unchanged can conceal a material
historical revision. A useful receipt records old and new identities and the
specific authorization or workflow that caused the replacement.

## Worked case A: materialize two historical days

The run-intervals command unpauses the finite daily DAG and waits for both known
scheduled runs to finish. It checks that each run's data interval corresponds to
its expected UTC day and that the two output files contain the correct synthetic
orders and totals. The check is not satisfied by any two successful run records;
the interval and source identities must match.

Max-active-runs and task concurrency limit how much historical work can execute
at once. A production backfill also needs an estimate of database load, API quotas,
queue occupancy and downstream effects. Running a large catchup immediately after
an outage can overload the same dependencies that are still recovering.

Repeated readback does not create new runs. The project separates inspection from
triggering so a learner can review saved history without replaying it. If a run
is still queued or failed, the command reports that state and preserves its
identity instead of creating a second run to hide the first result.

## Worked case B: correct one partition and preserve the other

The backfill-check action triggers the known correction workflow for the first
day using an explicit parameter. The fixture changes one amount under a new source
revision. The checker captures both partition identities before triggering,
requires the selected partition to show the corrected value and new identity,
and requires the second day's bytes to remain unchanged.

This is a bounded historical correction, not a claim that the public backfill CLI
or every possible timetable was exercised. The source explains how a general
backfill plan would select a range, choose reprocessing behavior and control
concurrency. The implemented case is intentionally one day so its effects can
be independently reconciled.

A downstream aggregate may now be stale even though the corrected partition is
right. Asset signals or an explicit dependency can request refresh, but the
consumer still needs a source/version contract. The next chapter studies that
orchestration signal separately from the underlying bytes. Do not infer that an
asset event proves every consumer already loaded the new revision.

## Mistakes, diagnosis and interview discussion

Write a backfill plan before triggering it: selected intervals, source versions,
expected outputs, dependency capacity, retry policy and rollback or correction
strategy. Avoid broad task clearing when only one partition needs repair. Inspect
actual scheduled and manual run semantics, because a supplied logical date does
not always define a manual run's data interval.

**Interview discussion: how do you rerun a historical day without double-counting?**
Select its exact source and interval, use an idempotent partition or table commit,
record the replacement revision and reconcile downstream aggregates. The two
cases show finite historical coverage and a targeted correction that proves
unrelated output stayed unchanged, rather than treating a successful trigger
response as proof of a completed data repair.

The [complete Airflow workshop](../../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
