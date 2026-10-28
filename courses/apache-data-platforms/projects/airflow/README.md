# Real Airflow TaskFlow workshop

This optional project runs Apache Airflow 3.3.2 as a finite local standalone
installation. It includes actual scheduled TaskFlow intervals, one intentional
retry, idempotent partition writes, a one-day correction, asset-triggered mapped
tasks with a one-slot pool, runtime SDK connection lookup and persistent history.
See [qualification](QUALIFICATION.md) for observed acceptance and pending gates.

The standalone SQLite topology is for local development. It does not prove a
production PostgreSQL metadata deployment, distributed worker availability or
remote service access. The main classroom pad reads the command notebooks and
never starts these services.

## Build and start on Linux, macOS or Windows/WSL2

Use a local Docker engine and Compose 2.28 or later. No host Python, compiler or
database is required. From the repository root, copy into a fresh owned directory:

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/airflow work/airflow
cd work/airflow
bash run.sh prepare
bash run.sh start
```

Normal preparation explicitly pulls the pinned upstream combined image for the
native Linux AMD64 or ARM64 architecture. Unsupported engines fail before pulling;
there is no automatic AMD64 emulation on ARM. Start uses only local prepared images.
The launcher prints a loopback UI address. This synthetic development installation
uses fixture user `learner` and password `learner`; it must remain local.

If that image cannot be obtained through a trusted path, an explicit fresh-copy
alternative builds an isolated virtual environment on an already prepared native
Core classroom image:

```bash
bash run.sh prepare --reuse-core
bash run.sh start
```

This route uses the architecture-specific hash lock and the applicable subset of
official Airflow 3.3.2 constraints. Its source URL and full upstream constraints
SHA256 are retained in `upstream.json`. It does not modify the ordinary Core
runtime or install packages during task execution. The distinct image and selected
route are retained in the private `.env` file; no route is silently switched.

The default host port is 18880. Before first preparation/start, a different loopback
port can be selected if that port is already occupied:

```bash
AIRFLOW_WORKSHOP_PORT=18881 bash run.sh prepare
bash run.sh start
```

Keep the saved `.env` to resume the same project. A port change is not inferred
from later environment values; use a separately owned fresh copy for a different
selection. The fixed port preserves the UI address during ordinary resume.

## Run the finite workflows

```bash
bash run.sh health
bash run.sh asset-check
bash run.sh retry-check
bash run.sh run-intervals
bash run.sh backfill-check
bash run.sh connection-check
bash run.sh readback
```

The DAGs begin paused. The daily producer explicitly selects CronDataIntervalTimetable and has only two
full-day scheduled UTC intervals,
January 1 and 2, 2026. The client waits for actual scheduler-created runs and checks
intervals and exact data. Its fail_once task intentionally fails the first attempt
and succeeds under its configured retry. A red first-attempt log is expected only
for that identified fixture task, never an excuse to ignore other failures.

The source has first-day amounts 4 and 9, and second-day amount 7. The explicit
one-day correction changes 4 to 6, producing first-day total 15 while retaining the
other partition byte-for-byte. Repeated inspection does not retrigger a successful
known manual run. A prior failed or ambiguous run is reported for diagnosis and
is not hidden behind a fresh identity.

The asset consumer maps east/west summary tasks through one configured pool slot.
Its receipts identify source versions actually observed; an early asset event may
see only the first available partition. The connection example resolves only a
local synthetic reference and rejects an absent identifier, without printing
credentials or claiming to connect to an external database.

## State, resume and replacement

```bash
bash run.sh stop
bash run.sh resume
bash run.sh health
bash run.sh readback
```

Resume reuses the exact retained container without a build or pull. Metadata,
logs, output partitions, attempt markers and source-bound observations live in an
owned named volume. The image contains dependencies; the copied folder contains
maintained source plus the independent project identity.

```bash
bash run.sh down
bash run.sh start
bash run.sh readback
```

Down removes only owned containers/network and retains the volume. Start can
replace containers while checking existing installation identity. Moving source
to another Docker engine does not migrate its volume or saved metadata.

`readback` is inspection only. It does not rerun workflows, restore source or
recreate missing output. Health checks inspect actual component statuses rather
than treating HTTP 200 as scheduler health. Use bounded logs before taking action:

```bash
bash run.sh status
bash run.sh logs
```

## Resource and cleanup boundary

The standalone service has a 2 GiB memory limit, two CPUs, a 384 process limit and 256 MiB
temporary storage. These are configured limits, not measured peak requirements.
Only a loopback host port is published; no engine socket, host credentials or
unrelated learner state is mounted. The SimpleAuth manager and plaintext fixture
password are development-only facilities.

Ordinary stop, resume, down and failures preserve data. Only this separate explicit
command deletes the verified owned disposable state:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Every affected container, network and volume must match ownership labels. No global
prune occurs. A PID-marked lock prevents concurrent lifecycle actions; inspect an
interrupted owner before manually removing only that stale lock. Keep source,
metadata, task logs and data-output observations distinct when reporting recovery.

The daily shorthand produced zero-duration trigger intervals in the first actual
qualification on this release/configuration. The source now selects the interval
timetable explicitly and rejects zero, partial or multi-day windows. Original
wrong-window metadata was retained as diagnostic evidence; it was not rewritten
or counted as successful interval acceptance.

## Reuse a published classroom base from Docker Hub

If the matching release is published, prepare the same local base alias without
rebuilding it. Replace `yourname` with the publisher's namespace. Docker selects
the native architecture from the combined manifest:

```bash
docker pull yourname/ds60sqlpy:1.0.0-worker-python-core
docker tag yourname/ds60sqlpy:1.0.0-worker-python-core ds60sqlpy-worker-python-core:1.0.0
```

Then use the explicit `--reuse-core` preparation in a fresh copied workshop. The
launcher still verifies the native image architecture. This pulls and locally
retags an existing PythonCore base; it does not push an image or rebuild that base.
The separate workshop dependencies are prepared by the explicit workshop command.
Combined worker tags include `worker-`; `1.0.0-python-core` is not this layout.
