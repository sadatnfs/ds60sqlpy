# PostgreSQL and analytical SQL

Run `./classroom --starter` from the course folder and choose **PostgreSQL**
from **All learning paths**. Docker supplies the PostgreSQL service and SQL
runner. You do not need a host database installation. Start with the
[setup guide](../../docs/one-command-classroom.md) on Linux, macOS or Windows WSL 2.

## Choose the right starting point

The SQL track contains **84 learning units**: the original 60 numbered lessons
and 24 named units that add a gentler entry, foundations, deeper analysis and
professional practice. The day numbers are labels, not deadlines.

New SQL learners should begin with the three small-fixture lessons in the
[professional guide](../professional/README.md): `sql-start-01` teaches tables
and result grain, `sql-start-02` teaches NULL and ordering, and `sql-start-03`
teaches query construction and debugging. Continue to `sql-01` when ready.
Follow the catalog's direct prerequisites, including foundation checkpoints
before later windows, schema evolution and operational lessons.

The numbered route develops selection, joins, grouping, subqueries, data
changes, types and dates, window functions, CTEs, JSON/XML, execution plans,
indexes, partitions and transaction behavior. Projects apply these mechanisms
to commerce, finance, warehousing, BI and a final analytical handoff.
Professional extensions cover relational design, migrations, security,
routines, types, testing, analytical correctness, recovery boundaries,
replication models, temporal data and concurrency. Six deeper units reinforce
relational reasoning, advanced aggregation, event sequences and query evidence.

## Run the intended artifact

Read the matching [companion guide](companion-guides/README.md), then select
**Whole SQL lesson (psql)** for a full course script. These files can contain
`psql` commands as well as SQL, so pasting them into a plain SQL snippet is not
equivalent. Use snippet mode for small ordinary SQL experiments.

The classroom keeps your editable learner copy separate from checked-in
references. Save, predict, run and inspect the transcript's first error and
exit status. Preserve `ON_ERROR_STOP` behavior and declared transaction
boundaries. Do not change a lesson's rollback into a commit merely to make
results persist. Follow the guide's explicit stateful workflow where needed.

The local disposable database is `advanced_sql_training`. A fresh classroom
uses `admin` / `admin` for its limited learning role. Confirm the actual project
and connection information through classroom status. Never point training
resets or lesson scripts at a shared or valuable database.

## Training setup and stateful projects

The explicit training reset establishes the standard fixtures. It replaces
course-owned training data and is not an everyday startup action. Most lesson
experiments clean up or roll back according to their own script. Warehouse
Days 52 through 54 deliberately form a stateful sequence; follow those guides
in order rather than resetting between steps. See
[PostgreSQL setup](../../docs/setup/postgresql.md) for the exact boundary.

## Keep your work

```bash
./classroom stop
./classroom resume
```

Resume uses the same project's local containers/images and retained volumes.
SQL pads, transcripts and progress live in the learning volume; database tables
live in the PostgreSQL volume. Back up both before an engine reset or machine
move using [the export guide](../../docs/docker-classroom.md#5-export-learning-work-and-the-database).

## Optional notebook and engineering work

Ordinary SQL study stays inside the classroom. A separately prepared
contributor can generate [guided SQL notebooks](../../docs/guided-sql-notebooks.md)
through the supported CLI; they run full scripts with `psql`. The dedicated
[JupySQL lesson](../../docs/setup/jupyter-postgresql.md) instead teaches
interactive `%sql` and `%%sql` cells. These are different execution contracts.

Connect SQL to application code in the [Python + PostgreSQL bridge](../../bridge/README.md).
Use [validation](../../docs/validation.md) when contributing. Structural checks,
one successful reference run and independent query reasoning are different
forms of evidence. Use hints and reference explanations to understand why a
query is correct, including cases where a plausible total hides duplicate rows.
