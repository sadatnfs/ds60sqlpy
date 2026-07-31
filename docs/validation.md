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

Sensitive-content guard:

```text
python scripts/scan_secrets.py --history
```

Practice enrichment, self-contained lesson depth, and generated portal drift:

```text
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
```

Add `--all` to print passing details as well as failures, warnings, and summaries. This command performs fast structural checks; it does not execute every notebook or SQL lesson.

On Windows, use:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}

& $CoursePython scripts\course.py doctor
& $CoursePython scripts\course.py catalog
& $CoursePython scripts\course.py validate
& $CoursePython scripts\scan_secrets.py --history
& $CoursePython scripts\audit_practice.py
& $CoursePython scripts\audit_lesson_depth.py
& $CoursePython scripts\build_course_guide.py --check
& $CoursePython scripts\build_lesson_readers.py --check
```

On macOS/Linux, use:

```bash
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py catalog
.venv/bin/python scripts/course.py validate
.venv/bin/python scripts/scan_secrets.py --history
.venv/bin/python scripts/audit_practice.py
.venv/bin/python scripts/audit_lesson_depth.py
.venv/bin/python scripts/build_course_guide.py --check
.venv/bin/python scripts/build_lesson_readers.py --check
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
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks
uv run --no-sync pytest
```

## Maintainer checks

Core setup installs the quality tools used by continuous integration:

```text
python scripts/build_catalog.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python -m pytest tests/test_course_guide.py tests/test_lesson_depth_audit.py tests/test_lesson_reader.py tests/test_portal.py tests/test_sql_notebook.py tests/test_windows_startup.py
python -m ruff check src scripts tests bridge python/professional
python -m mypy
python -m pytest
python scripts/course.py validate
python scripts/scan_secrets.py --history
```

Review the regenerated catalog diff. CI runs these core checks on Python 3.12
for Windows, macOS, and Linux and on Python 3.11 for Linux, then executes the
full SQL sequence separately against PostgreSQL 17. Each matrix leg sets
`UV_PYTHON` to the requested version and asserts `sys.version_info[:2]` after
sync, so the learner-default `.python-version` cannot silently collapse the
matrix onto Python 3.12. The Windows core runner also registers
`Python (ds60sqlpy)` and runs
`start_ds60.ps1 -DiagnosticsOnly -NonInteractive -SkipPostgreSql`, exercising
the native startup under Windows PowerShell 5.1 and the
both-environment-layout readiness path without opening a browser.

The focused learner-entry tests cover different boundaries:

- `test_course_guide.py` checks dashboard catalog links, generated copy, and
  that all 154 guide-authored Codex prompts are embedded without fallback
  drift.
- `test_lesson_depth_audit.py` checks the curriculum-wide beginner-depth
  contract, duplicate/template guards, runnable guide fences, and report.
- `test_lesson_reader.py` checks deterministic rendered pages, safe link
  rewriting, recursive Markdown/SQL reference pages, mode-specific completion
  controls, and stale-page removal.
- `test_portal.py` checks loopback/token/origin/path/launch restrictions and
  exact artifact commands.
- `test_sql_notebook.py` checks stable SQL IDs, paths below `.learning/sql/`,
  no-overwrite behavior, fixed `psql` invocation, database/reset guards,
  bounded transcripts, and stateful prerequisite preparation.
- `test_windows_startup.py` statically checks the double-click launcher and
  PowerShell 5.1 orchestration. Native execution remains a Windows CI
  boundary.

Unit tests do not replace browser QA. For a learner-experience change, open
both `file://.../START_HERE.html` and the private `127.0.0.1` portal. Verify a
Python, SQL, and bridge card; guide/learner/solution tabs; keyboard navigation;
desktop and narrow layouts; no raw `.md`, `.ipynb`, `.py`, or `.sql` browser
view; rendered setup/reference navigation; dashboard-only static completion;
the loopback lesson checkbox; no unexpected network requests; and the exact
run controls available in each mode. Do not click an action that would reset
PostgreSQL.

The sensitive-content scan is deliberately offline and reports only an object
ID, path, line number, and finding category so it does not copy a suspected
credential into logs. It catches common token/key formats, private-key files,
credential-bearing URLs, ignored credential-shaped local files, and reachable
Git-history blobs. Its narrow fixture allowances are covered by tests. It is a
guardrail, not proof against every secret format; still review changes and use
an organization scanner when available.

Every push and pull request also runs the actual learner setup flow on fresh
Windows, macOS, and Ubuntu Python 3.12 runners, reruns doctor through the
generated `.venv`, and checks that setup produced no trackable files. macOS and
Ubuntu execute `setup.sh`. Windows first previews
`bootstrap_windows.ps1 -SkipPostgreSql -WhatIf`, then executes the same
bootstrapper in locked mode. Both Windows invocations use the built-in Windows
PowerShell 5.1 host. This exercises discovery, native-command argument handling,
environment creation, locked dependency installation, kernel registration,
both supported `.venv` layouts, and doctor without requiring PostgreSQL on the
CI image.

The weekly and manually dispatched heavy job validates the lock, installs every
extra, then exercises the maintained advanced import manifest for the `bridge`,
`professional`, `sql-notebooks`, `ml`, `production`, `deep-learning`, `nlp`,
and `geo` lesson stacks on fresh Windows, Ubuntu, and macOS Python 3.12
runners:

```text
uv sync --frozen --all-extras
uv run --no-sync python scripts/check_advanced_imports.py
```

Each import runs in an isolated process and does not fetch datasets, pretrained
weights, spaCy pipelines, or external services. This proves locked package
installation and basic import compatibility on those platforms; it does not
prove model training, GPU support, asset availability, live APIs, or every
advanced lesson's runtime behavior. A fast core-job dry run also proves that
the all-extras lock has an installable plan for Windows x86-64, Linux x86-64,
Intel macOS, and Apple Silicon before the heavy job starts. The ML extra
constrains Numba by platform because SHAP's transitive requirement is otherwise
broad enough for a legacy source release with incomplete Python-version
metadata to enter a valid-looking lock. PyTorch and TorchVision are likewise
paired by macOS architecture because current PyTorch releases no longer ship
Intel-macOS wheels and now require macOS 14 for Apple Silicon. The macOS heavy
job installs Homebrew's `libomp` first, matching the documented learner setup
and allowing the locked LightGBM and XGBoost binaries to load.

`Advanced imports` intentionally does **not** run for an ordinary push or pull
request because installing every optional package is the slowest workflow
surface. To run it immediately, follow GitHub's
[manual workflow instructions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow):

1. Open **Actions**.
2. Select **Course validation**.
3. Choose **Run workflow**, select the branch containing the changes, and
   confirm **Run workflow**.
4. Open that run and watch the three `Advanced imports` matrix jobs.

GitHub dispatches the whole workflow; its UI cannot start only one job inside a
workflow. The `workflow_dispatch` event is what makes the advanced job eligible
while the normal core, learner-bootstrap, and PostgreSQL jobs also run. With the
GitHub CLI installed, the equivalent command is:

```text
gh workflow run ci.yml --ref <branch-name>
```

## Local validation evidence (2026-07-30)

The comprehensive local run recorded this evidence:

- Locked Python 3.12 suite: **440 passed, 3 expected skips**, plus **10
  unittest subtests**. Two skips require native PowerShell and one requires a
  process-pool semaphore unavailable in the local sandbox.
- Ruff lint/format passed, and mypy checked **89 source files** without an
  error.
- `uv.lock` resolved **376 packages**; frozen all-extras dry runs succeeded for
  Windows x86-64, Linux x86-64, Intel macOS, and Apple Silicon.
- PostgreSQL 16.14: **72/72 learner scripts** and **72/72 executable
  solutions** passed; focused SQL runner/contract/semantic tests passed
  **153/153**.
- The JupySQL solution notebook executed **18/18 code cells**, including
  **9/9 live SQL cells**, against only the local disposable course database.
- Notebook structure/syntax checks passed **122/122**, and offline smoke checks
  passed **13/13**.
- Practice coverage and lesson-depth audits each passed **154/154 lessons**.
- Generated-reader checks passed for `START_HERE.html`, **154 lesson pages**,
  and **39 recursively linked reference pages**.
- Interactive private-portal browser QA passed at desktop and narrow
  breakpoints with no horizontal page overflow, raw source links, or console
  warnings. The sandboxed test browser blocks `file://` navigation, so static
  USB mode is covered here by deterministic DOM/link tests and isolated
  generation rather than a live `file://` session.
- The current-tree and reachable-Git-history sensitive-content scan passed.

Native Windows PowerShell 5.1 execution and the Linux Python 3.11 matrix remain
CI-only boundaries for this snapshot. These results describe this checkout and
environment on the stated date; they are evidence, not a promise that later
revisions or other machines will produce the same results.

## Validation layers

### 1. Inventory and structure

Check:

- `curriculum/catalog.json` is valid JSON and matches a fresh run of `python scripts/build_catalog.py`.
- Every catalog path exists.
- Lesson IDs and ordering are unique.
- Declared companion guides and solutions exist.
- Notebook files are valid JSON and valid `nbformat`.
- Markdown internal links resolve.
- Every lesson surface meets its immutable
  `curriculum/practice_baseline.json` doubling target.
- Every cataloged lesson passes `scripts/audit_lesson_depth.py`: complete
  beginner-facing sections, definitions, worked examples, exercise
  verification contracts, explanatory solutions, historical Python notebook
  depth, and a context-rich per-lesson Codex coaching prompt.
- `docs/practice-coverage.md` and `docs/lesson-depth-report.md` match their
  generators.
- `START_HERE.html` matches a fresh deterministic portal render.
- `lesson-pages/` contains exactly one current page per cataloged lesson and
  matches a fresh deterministic reader render.
- `reference-pages/` matches the recursive closure of local Markdown/SQL links
  reachable from the dashboard and rendered course artifacts.
- No user-facing local Markdown or SQL link in the generated HTML surfaces
  opens raw browser source.
- The loopback portal rejects hidden files, invalid tokens, cross-origin
  mutations, unknown lesson IDs, and non-allowlisted launch actions.
- Static pages remain self-contained/read-only; loopback pages receive only
  the session token needed for fixed catalog-resolved actions.
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
- SQL-magic cells are structurally checked through notebook tags; live
  PostgreSQL execution is recorded separately.

Run the notebook-aware validator after installing the core environment:

```text
python scripts/validate_notebooks.py
python scripts/validate_notebooks.py --smoke
```

The normal smoke set excludes the live PostgreSQL notebook. After setting
`DS60_DATABASE_URL` to the disposable database, execute its solution from a
clean kernel:

```powershell
# Windows PowerShell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}

& $CoursePython -m nbconvert --execute --to notebook `
    --output-dir .\artifacts\notebook-validation `
    .\bridge\professional\solutions\bridge_jupyter_01_postgresql_magics_solution.ipynb
```

```bash
# macOS/Linux
.venv/bin/python -m nbconvert --execute --to notebook \
  --output-dir artifacts/notebook-validation \
  bridge/professional/solutions/bridge_jupyter_01_postgresql_magics_solution.ipynb
```

The executed copy belongs under ignored `artifacts/`; keep the checked-in
notebook output-free.

Cleared notebook outputs are normal. Record execution evidence in validation logs or CI rather than committing noisy, machine-specific output.

#### Guided per-lesson SQL notebooks

These learner-local notebooks are generated from stable SQL catalog IDs and
run complete scripts through `psql`; they are not the checked-in JupySQL
magics lesson. Validate their safety and generation contract without writing
into a learner's existing `.learning/` directory:

```text
python -m pytest tests/test_sql_notebook.py tests/test_portal.py
```

The tests use isolated temporary repositories. They must prove valid
notebook/kernelspec structure, no absolute checkout path or connection value,
catalog-only source selection, no overwrite of learner files, fixed
non-shell `psql -f`, unchanged line-start and inline meta-commands/includes, the
`advanced_sql_training` restriction, and explicit reset confirmation.

When manually exercising a generated notebook, first preserve any existing
`.learning/sql/<lesson-id>/` work. Report separately whether generation,
Jupyter launch, database preparation, learner SQL execution, and
`00_verify.sql` succeeded. A rendered reader or structurally valid generated
notebook is not evidence that PostgreSQL authentication or the lesson query
succeeded.

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

Named professional SQL modules live under `sql/professional/`. Run the
learner and solution artifact in separate clean sessions. Role administration,
extensions, physical recovery, and replication modules include capability
boundaries; report an instructional skip separately from the default
rollback-safe SQL that did execute.

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
python -m pytest bridge/professional/tests
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

### 6. Professional Python modules

Run the professional solution tests independently from the learner scaffolds:

```text
python -m pytest python/professional/tests
```

Package-build tests install only into a temporary target. Arrow/DuckDB tests
use generated local files. HTTP, concurrency, AI, analytics, migration, and
service tests use deterministic fakes or local fixtures. No professional
default test should require a public endpoint, hosted model, cloud account, or
credential.

### 7. Platform checks

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

5. When lessons or portal behavior changed, regenerate the maintained outputs:

   ```text
   python scripts/audit_practice.py --write-report
   python scripts/build_course_guide.py
   python scripts/build_lesson_readers.py
   git diff -- docs/practice-coverage.md START_HERE.html lesson-pages/
   ```

6. Run `python scripts/course.py validate`.
7. Run:

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
