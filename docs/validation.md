# Validation

Validation separates structural confidence from actual execution. A notebook that parses has not necessarily run; a SQL file that looks plausible has not necessarily succeeded against PostgreSQL.

Run commands from the repository root.

## Standard commands

Environment:

```text
python scripts/course.py doctor
```

Catalog:

```text
python scripts/course.py catalog
```

Repository validation:

```text
python scripts/course.py validate
```

Add `--all` to print passing details as well as failures, warnings, and summaries. This command performs fast structural checks; it does not execute every notebook or SQL lesson.

On Windows, use:

```powershell
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe scripts\course.py catalog
.\.venv\Scripts\python.exe scripts\course.py validate
```

On macOS/Linux, use:

```bash
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py catalog
.venv/bin/python scripts/course.py validate
```

The course CLI uses the standard library for pre-install inspection so catalog and environment diagnostics remain available before third-party packages are installed.

The learner setup scripts install compatible dependency ranges with `pip`.
Continuous integration uses the checked-in cross-platform `uv.lock` and rejects
lock drift:

```text
uv lock --check
```

Maintainers with `uv` can reproduce the CI core environment with:

```text
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality
uv run --no-sync pytest
```

## Maintainer checks

Core setup installs the quality tools used by continuous integration:

```text
python scripts/build_catalog.py
python -m ruff check src scripts tests bridge
python -m mypy
python -m pytest
python scripts/course.py validate
```

Review the regenerated catalog diff. CI runs these core checks on Python 3.12
for Windows, macOS, and Linux, then executes the full SQL sequence separately
against PostgreSQL 17.

Every push and pull request also runs the actual learner `setup.ps1` or
`setup.sh` flow on fresh Windows, macOS, and Ubuntu Python 3.12 runners, reruns
doctor through the generated `.venv`, and checks that setup produced no
trackable files.

The weekly and manually dispatched heavy job resolves, installs, and imports
every direct package in the `bridge`, `ml`, `production`, `deep-learning`,
`nlp`, and `geo` extras on fresh Windows and Ubuntu Python 3.12 runners:

```text
uv sync --frozen --all-extras
uv run --no-sync python scripts/check_advanced_imports.py
```

Each import runs in an isolated process and does not fetch datasets, pretrained
weights, spaCy pipelines, or external services. This proves locked package
installation and basic import compatibility on those two platforms; it does
not prove model training, GPU support, asset availability, live APIs, or every
advanced lesson's runtime behavior. macOS receives the core matrix but not this
heavy all-extras gate.

## Validation layers

### 1. Inventory and structure

Check:

- `curriculum/catalog.json` is valid JSON and matches a fresh run of `python scripts/build_catalog.py`.
- Every catalog path exists.
- Lesson IDs and ordering are unique.
- Declared companion guides and solutions exist.
- Notebook files are valid JSON and valid `nbformat`.
- Markdown internal links resolve.
- No unexpected generated artifacts are tracked.

This layer is fast but does not prove lesson semantics.

### 2. Python import and notebook smoke checks

Check:

- Direct imports are declared in the appropriate dependency group.
- Notebook kernelspec metadata is consistent.
- Representative example cells run from a clean kernel.
- Exercise notebooks do not depend on hidden execution order.
- Expected failure demonstrations fail for the documented reason.
- Heavy or network-tagged cells are reported distinctly.

Run the notebook-aware validator after installing the core environment:

```text
python scripts/validate_notebooks.py
python scripts/validate_notebooks.py --smoke
```

Cleared notebook outputs are normal. Record execution evidence in validation logs or CI rather than committing noisy, machine-specific output.

### 3. Offline checks

After disclosed first-run caches:

- Block or disconnect network access.
- Run core notebooks.
- Require missing optional model caches to produce an actionable skip or error.
- Confirm no lesson silently fetches a dataset or package.

See [Offline use](setup/offline.md).

### 4. SQL execution

Canonical automation uses PostgreSQL 17; supported learner environments are PostgreSQL 16+.

Cross-platform Compose execution:

```text
docker compose up -d postgres
docker compose run --rm sql-runner -f sql/postgres-60day/00_setup.sql
docker compose run --rm sql-runner -f sql/postgres-60day/00_verify.sql
docker compose run --rm sql-runner -f sql/postgres-60day/day01_select_where_orderby.sql
docker compose down
```

`00_setup.sql` is destructive within the course-owned `training` schema. The Compose database is disposable, but still resolve the target before running setup. `docker compose down` preserves its named volume.

Reset only the disposable training database:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
```

Run a lesson:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

Check:

- Setup completes from a clean database.
- Setup produces the deterministic relationships and expected row counts checked by `00_verify.sql`; generated dates intentionally remain relative to `CURRENT_DATE`.
- Each independent day runs in a new `psql` session.
- Rollback leaves no unexpected persistent state.
- The Day 52–54 warehouse project is the declared stateful exception: Day 52 resets and commits the course-owned `dwh` schema, then Days 53 and 54 run in order.
- Executable solutions, where declared, run against the same schema.

Do not drop `ON_ERROR_STOP`; without it, statement errors can be missed.

### 5. Engineering bridge

The bridge's default validation does not require a database:

```text
python -m pytest bridge/tests
python -m compileall -q bridge
```

Check:

- learner and solution modules parse on Python 3.11 and 3.12;
- fake-backed tests cover configuration, parameters, transactions, retries,
  ETL accounting, async bounds, and capstone failure behavior;
- examples do not hard-code credentials or silently connect;
- optional live work reads `DS60_DATABASE_URL`, targets only the disposable
  course database, and documents its rollback or cleanup boundary.

Fake-backed success does not prove server permissions, network behavior, or a
real query plan. Label a live PostgreSQL check separately when one is run.

### 6. Platform checks

Core setup and doctor should run on:

- Windows with PowerShell
- macOS
- Linux

Verify activation-free Windows commands. Test platform-sensitive packages separately from the core curriculum.

## During development

Use focused checks first, then the full validation:

1. Validate the changed notebook, guide, or SQL file.
2. Validate its generated catalog entry and links.
3. Run its prerequisite and successor smoke checks.
4. Regenerate the catalog when artifact names or catalog-builder metadata changed:

   ```text
   python scripts/build_catalog.py
   git diff -- curriculum/catalog.json
   ```

5. Run `python scripts/course.py validate`.
6. Run:

   ```text
   git diff --check
   git status --short
   ```

Do not reformat unrelated notebooks or SQL files merely to make a focused validation pass.

## Interpreting results

Use precise labels:

- **Structure validated:** the artifact parses and paths resolve.
- **Smoke tested:** representative behavior ran.
- **Fully executed:** the intended runnable artifact completed in the documented environment.
- **Offline validated:** it completed with network unavailable after disclosed bootstrap.
- **Not validated:** state the exact missing dependency, service, platform, or cache.

Never report “all tests pass” when heavy, network, Windows, or SQL checks were skipped.

## Adding a validator

A validator should:

- Be deterministic
- Work from the repository root
- Avoid changing learner artifacts
- Produce a nonzero exit status on failure
- Explain the file and remediation
- Distinguish unavailable optional prerequisites from defects
- Run without network unless explicitly testing connected bootstrap

Update this document, the course CLI, CI, and applicable `AGENTS.md` together.
