# Guided SQL lesson notebooks

Every cataloged SQL lesson and executable SQL solution can become a private,
guided Jupyter notebook. The notebook is generated only by an explicit learner or contributor request, under the Git-ignored `.learning/sql/` directory.

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

## Choose the classroom or a prepared notebook environment

For normal study, run `./classroom`, select SQL and choose the lesson. The
snippet and whole-lesson pads are distinct workspaces. Use the whole-lesson
mode for complete scripts with reviewed `psql` commands. No host Jupyter,
Python or PostgreSQL installation is required for that Docker route.

The guided notebook is an optional contributor/editor workflow. It uses a
separately prepared POSIX environment, also available inside WSL 2. Follow
[CONTRIBUTING.md](../CONTRIBUTING.md) and [PostgreSQL setup](setup/postgresql.md)
to prepare its interpreter, `psql` and disposable local database connection.
Obtain the database's actual published port with `./classroom status`; do not
assume port 5432. Keep credentials in the private client environment or password
file, never in the notebook or checked-in editor settings.

Generate a learner notebook, or explicitly request the solution notebook:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-01
uv run --no-sync python scripts/course.py sql notebook sql-01 --artifact solution
```

The focused generator exposes the same contract:

```sh
uv run --no-sync python scripts/build_sql_lesson_notebook.py sql-01
```

The command prints the notebook and editable SQL paths. Open that generated
notebook in your prepared editor or JupyterLab, select the intended contributor
interpreter and follow its readiness cells. The retired native portal does not
launch notebook processes. The local notebook workspace is separate from
Docker-volume pads and does not synchronize them automatically.

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

1. **Goal and three-program mental model** - identifies the lesson, guide,
   official source, editable copy, and the separate roles of Jupyter, Python,
   `psql`, and the PostgreSQL server.
2. **Before-you-run checklist** - confirms the selected course kernel, local
   tools, disposable database name, and the difference between reading and
   execution.
3. **Secret-free readiness** - locates the repository, validates the database
   target, and explains each pass, warning, or failure.
4. **Study and edit** - renders the official SQL for comparison and points to
   the preserved editable copy.
5. **Explicit preparation** - requires the learner to confirm the destructive
   reset switch before preparing the course schema.
6. **Run and inspect** - executes the complete copy through fixed `psql -f`,
   then teaches the learner to read the exit status, transcript, result
   columns, row grain, counts, and ordering.
7. **Checks and recovery** - reruns deterministic database invariants and maps
   common failures to the responsible layer.
8. **Reflection and next step** - asks for evidence in the learner's own words
   before progress is recorded.

The notebook is deliberately more than a wrapper around a command. It teaches
how to tell whether a query ran, where output came from, why the database is
safe to reset, and what evidence should be captured before a learner edits
again.

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
Configure the local client environment or private password file before starting
Jupyter. Windows users prepare that client inside WSL 2. Never put a password
in notebook content, metadata or repository files.

Database preparation is deliberately a separate cell with
`CONFIRM_COURSE_RESET = False`. Change it to `True` only after reading the
warning. The runner then:

1. executes the fixed `sql/postgres-60day/00_setup.sql`;
2. executes the fixed `sql/postgres-60day/00_verify.sql`; and
3. executes earlier members of the selected lesson's declared stateful group.

The third step matters for Days 52–54: opening Day 54 prepares Days 52 and 53
in order. Other lessons receive the clean seed schema without replaying dozens
of unrelated scripts.

The notebook runner constrains paths and client-side `psql` commands; it is not
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

Contributor and editor integrations call:

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
