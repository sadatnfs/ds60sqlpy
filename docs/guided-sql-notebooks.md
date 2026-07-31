# Guided SQL lesson notebooks

Every cataloged SQL lesson and executable SQL solution can become a private,
guided Jupyter notebook. The notebook is generated only when the learner opens
it, under the Git-ignored `.learning/sql/` directory.

This workflow is different from copying a `.sql` file into a `%%sql` cell.
Course scripts can contain `psql` commands such as `\ir`, `\if`, `\gset`, and
`\echo`. JupySQL does not implement those commands. The guided notebook renders
the source for reading and runs the editable working copy with:

```text
psql -X --no-password -v ON_ERROR_STOP=1 --pset pager=off -f <fixed-working-copy>
```

There is no shell and no free-form path parameter. Lesson IDs, official source
files, solution files, and learner-local output paths all come from the course
catalog.

## First-time Windows path

From a PowerShell window opened in the repository:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1

$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}

& $CoursePython scripts\course.py doctor
& $CoursePython scripts\course.py portal
```

Keep that PowerShell window open. The bootstrap adds a discovered PostgreSQL
installation to the current process path, and Jupyter launched from the portal
inherits it. If the notebook says `psql` is missing, close Jupyter, return to
this PowerShell window, rerun the doctor, and start the portal again.

The normal portal action is the easiest route: choose a SQL lesson and select
the guided notebook action. The action creates an editable SQL copy and a
notebook, then opens the notebook in JupyterLab.

## macOS and Linux path

```bash
bash scripts/setup.sh --advanced
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py portal
```

Start the portal from the terminal where `psql` and any
`DS60_DATABASE_URL` value are available.

## Generate without the portal

The same catalog-restricted generator is available from the course CLI:

```powershell
# Windows PowerShell
& $CoursePython scripts\course.py sql notebook sql-01
& $CoursePython scripts\course.py sql notebook sql-01 --artifact solution
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py sql notebook sql-01
.venv/bin/python scripts/course.py sql notebook sql-01 --artifact solution
```

The focused script exposes the same contract:

```text
python scripts/build_sql_lesson_notebook.py sql-01
python scripts/build_sql_lesson_notebook.py sql-01 --artifact solution
```

Only stable SQL IDs in `curriculum/catalog.json` are accepted. The current
catalog has one executable `.sql` solution for each SQL module. The optional
`--solution-index` is one-based so the contract remains deterministic if a
future module gains more than one.

## What the generated workspace contains

For `sql-01`, the generated files are:

```text
.learning/
└── sql/
    └── sql-01/
        ├── lesson/
        │   ├── guided.ipynb
        │   └── workspace/sql/postgres-60day/day01_select_where_orderby.sql
        └── solution-1/
            ├── guided.ipynb
            └── workspace/sql/postgres-60day/solutions/day01_solutions.sql
```

The notebook follows this learning sequence:

1. **Goal** — identifies the lesson, guide, official source, and editable copy.
2. **Setup** — locates the repository and performs a secret-free readiness
   check.
3. **Steps** — renders the official SQL, links to the editable copy, prepares
   the database, and runs the complete working file.
4. **Checks** — reruns deterministic course database invariants.
5. **Next Steps** — sends the learner back to progress tracking and the next
   catalog prerequisite.

Generation never overwrites an existing notebook or SQL copy. Reopening a
lesson therefore preserves experiments and notes. To start over, first save
anything worth keeping, remove only that lesson's `.learning/sql/<lesson-id>/`
directory, and reopen the cataloged artifact.

The workspace mirrors the source's repository-relative location. Fixed
recursive `\ir` dependencies are copied into that mirror so their relative
paths keep exactly the same meaning. Before execution, the runner confirms that
every executable `psql` meta-command segment still matches the catalog source,
including a command placed after SQL on the same line, and that included
dependency files are unchanged. Backslashes inside SQL strings, quoted
identifiers, dollar quotes, and comments are distinguished from executable
client commands. Learners can edit SQL exercises, but cannot turn the notebook
action into an arbitrary `\!` command or redirect an include to another file.

## Database safety

Notebook execution is restricted to the database named
`advanced_sql_training`. It accepts either that literal local database name or
a local-socket/loopback `postgresql://` or `postgres://` URL whose path names
that database. The only accepted URI query option is `sslmode`; the runner
rejects:

- a different database name;
- remote or multi-host authorities;
- key-value connection strings;
- non-PostgreSQL URL schemes;
- URL fragments; and
- routing, service, file-reading, or other unsupported URL query options.

If `DS60_DATABASE_URL` is unset, native local PostgreSQL connection defaults
apply to `advanced_sql_training`. If it is set, the value stays in the Jupyter
process environment: the notebook does not embed, print, or save it. The runner
passes the validated target to libpq through the child environment rather than
a visible command argument, and uses `--no-password` so a kernel cannot hang at
an invisible password prompt.
Configure native authentication, a local password file, or the disposable
Compose URL before starting the portal.

Database preparation is deliberately a separate cell with
`CONFIRM_COURSE_RESET = False`. Change it to `True` only after reading the
warning. The runner then:

1. executes the fixed `sql/postgres-60day/00_setup.sql`;
2. executes the fixed `sql/postgres-60day/00_verify.sql`; and
3. executes earlier members of the selected lesson's declared stateful group.

The third step matters for Days 52–54: opening Day 54 prepares Days 52 and 53
in order. Other lessons receive the clean seed schema without replaying dozens
of unrelated scripts.

The launcher constrains runner paths and client-side `psql` commands; it is not
an SQL sandbox. An editable exercise can still contain database statements
with server-side effects, especially when PostgreSQL is running under a
superuser role. Never paste untrusted SQL. Use only the disposable course
database and a least-privileged course role for lessons.

## When to use JupySQL instead

Use the guided notebook for complete course scripts, exercises, DDL, projects,
and solutions. It preserves real `psql` behavior and shows a bounded transcript.

Use the checked-in
`bridge/professional/notebooks/bridge_jupyter_01_postgresql_magics.ipynb`
lesson for short, bounded exploratory queries, result-to-DataFrame conversion,
parameter binding, and explicit SQLAlchemy transaction ownership. See
[PostgreSQL in Jupyter](setup/jupyter-postgresql.md) for that separate workflow.

## Maintainer contract

Portal and editor integrations should call:

```python
generate_sql_notebook(catalog, lesson_id, artifact_kind, solution_index)
```

The function returns a `SqlNotebookWorkspace` with the generated notebook and
editable SQL paths. Callers must not accept a filesystem path or shell command
from the browser. Notebook execution uses `run_sql_workspace`, which computes
the same path from the catalog identity and rejects missing files, symlinks,
and paths outside `.learning/sql/`.

Generated notebooks are validated as nbformat 4.5, use the `ds60sqlpy` kernel,
contain no saved output, and contain no absolute repository path or connection
credential.
