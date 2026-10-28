## Orchestration records work and dependencies

Airflow schedules and tracks workflows. A DAG describes tasks and their dependency
relationships; a Dag Run is one instantiation, and task instances carry the state
of individual work for that run. Airflow is not the bulk-data processing engine
inside every task. A task can submit a query, write one partition or call another
system while Airflow records its attempt, dependencies and outcome.

TaskFlow decorators turn Python functions into scheduled task definitions. Calling
a decorated task while defining the DAG creates a dependency object rather than
immediately running the function's body. Small return values can travel through
XCom metadata; large tables should remain in an explicitly managed data system,
with a bounded reference passed between tasks.

The workshop uses Airflow 3.3.2 and imports the public TaskFlow API from airflow.sdk.
It runs an actual local standalone installation with persistent SQLite metadata,
logs and outputs. This is a development topology, not a production PostgreSQL
or distributed-worker deployment. The Docker project keeps these state categories
outside its image and publishes its teaching UI only on loopback.

## Worked case A: process two explicit daily intervals

The daily orders DAG uses an explicit CronDataIntervalTimetable, a fixed UTC
start, a finite historical end and catchup
enabled. It begins paused. The run-intervals action unpauses only that owned DAG
and waits for the two known historical data intervals. Each interval selects
synthetic source orders using a half-open window \([a,b)\), writes a versioned
partition and returns a small source-bound reference.

A schedule shorthand alone is insufficient evidence of interval shape. Initial
qualification of this selected release/configuration showed zero-duration trigger
intervals for the daily shorthand. The project therefore selects the data-interval
timetable explicitly and checks that each actual interval spans exactly one UTC
day. It preserves that observed distinction rather than silently treating a green
run as proof of a full-day population.

The data interval identifies the records the run is meant to process. It is not
the wall-clock time when a worker starts. For a daily schedule, a run normally
becomes eligible after its interval has ended. The workflow records the selected day and source identity, while readback exposes
actual interval start/end, logical date, run-after time and run identity. In the
qualified first interval, logical date is January 1, interval is January 1 through 2,
and the generated run identifier contains January 2. Do not derive a population
by splitting the run-ID string; inspect the real interval fields.

The checker inspects actual metadata states and exact partition values. A successful
Python function called outside Airflow would not prove scheduler behavior, task
state transitions or XCom wiring. Conversely, a green Dag Run without output
readback would be insufficient to prove the intended data was written.

## Worked case B: explain why now changes a backfill

The worked source contrasts the task's interval-based selection with a deliberately
shown wall-clock alternative. If a January partition is recomputed months later
using the worker's current date, it can select an empty or different population.
The correct source selection stays tied to the requested interval and source
version, so rerunning at a later wall time preserves its meaning.

For a deterministic hand-derived comparison, take February 1, 2026 as the later
wall-clock date. That incorrect date filter selects zero fixture rows and total 0;
the intended first-day orders 1 and 2 total 13. These numbers are a reasoning trace,
not a second Airflow execution. The actual task uses the real interval context
supplied by its scheduled run.

Manual triggering introduces another distinction. A supplied logical date is not
universally equivalent to a manually triggered run's data interval; the timetable
and trigger path determine that behavior. The correction workflow therefore uses
an explicitly validated day parameter for manual work instead of silently inferring
it from a timestamp whose semantics may differ.

## Mistakes, diagnosis and interview discussion

Avoid network calls, large reads and mutable side effects at DAG parse time.
The scheduler and DAG processor may parse definitions repeatedly, so top-level
execution is not a once-only initialization hook. Declare dependencies clearly,
keep XCom values small and inspect task states separately from data quality.
An orchestration success is not a scientific-validity guarantee for its output.

**Interview discussion: what is the difference between logical date and execution
time?** Logical date identifies the run in its scheduling model, often the interval
start for a scheduled timetable; actual execution can occur later because of
capacity, retries or backfill. These cases connect real interval-driven outputs
to actual metadata and explain why wall-clock selection breaks reproducibility.

The [complete Airflow workshop](../../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
