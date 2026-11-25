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
[shared receipt rules](../../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

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
