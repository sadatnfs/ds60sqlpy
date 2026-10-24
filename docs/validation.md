# Validation and release readiness

Validate the exact revision being shipped. Configuration, structural checks,
unit tests, real runtime execution and browser behavior answer different
questions. A passing parser does not prove a lesson runs, and a configured
workflow does not prove that its hosted jobs passed.

Run commands from the repository root. Keep learner projects and their Docker
volumes separate from disposable validation projects. Use the current workflow
run and its artifacts as evidence for that revision, rather than copying old
machine timings or test counts into documentation.

## Prepare a development environment

Learners need the Docker classroom. Maintainers running host checks also need
Python 3.12, the locked development dependencies and Node.js. The workflow uses
Node 24 for the framework-free UI checks. Python 3.11 remains a supported core
validation target; inspect `.github/workflows/ci.yml` for the exact matrix.

With `uv` installed:

```text
uv lock --check
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks --extra mcp
uv run --no-sync python scripts/course.py doctor
```

Prefix the Python commands below with `uv run --no-sync`, or use the interpreter
inside this checkout's `.venv`. On Windows, WSL 2 provides the same Bash and
Docker workflow as Linux. Optional native PowerShell setup is documented
separately and must not be confused with Windows Docker qualification.

Core setup does not install every heavy learning dependency. A test that needs
an optional compiler, framework, SQL service or model asset must either run in
its prepared environment or report that boundary explicitly.

## Fast checks during development

Run the narrow tests for the changed area first, then verify the maintained
source and generated views:

```text
python scripts/build_catalog.py
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/normalize_lesson_prose.py
python scripts/check_content_rendering.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
python scripts/build_journey_preview.py --check
python scripts/check_modules.py
python scripts/validate_notebooks.py
node scripts/check_classroom_ui.mjs
python -m ruff check src scripts tests bridge python/professional
python -m ruff format --check src scripts tests bridge python/professional
python -m mypy
python scripts/scan_secrets.py --history
git diff --check
```

`normalize_lesson_prose.py` is a dry check by default. When deliberately
refreshing reviewed prose, run it with `--write` after authoring generators and
before HTML generation. `check_content_rendering.py` renders the actual
published Markdown and notebooks, checking mathematics and code blocks through
the production reader. A generic Markdown parser is not a substitute.

After an intentional content change, regenerate the catalog, reports and
readers with `make generate`, or run that target's listed Python commands when
Make is unavailable. Review the generated diff. Never hand-edit maintained
HTML to hide source drift. The journey preview is a developer design archive;
the live `/classroom`, `/learn` and `/journeys` URLs use one shared interface.

The secret scanner reports categories and locations without copying suspected
credentials into logs. It checks the current tree and reachable Git history.
Keep private progress, work directories, caches and environment files out of
source control and release archives. Source cleanup does not remove material
already published in Git history; historical findings require a separate
reviewed response.

## Run tests in parallel

Use four grouped workers by default:

```text
python -m pytest -n 4 --dist loadgroup
```

The equivalent Make targets are:

```text
make test
make test TEST_WORKERS=2
make test-serial
```

Keep `--dist loadgroup`. Tests that use the same disposable PostgreSQL fixtures
belong to the `shared-postgres` group and run serially within that group. The
suite rejects unsafe distribution when those shared fixtures are enabled.
Changing the scheduler can cause destructive fixture races even if individual
tests pass. Use `-n 0` for focused serial diagnosis, and reduce worker count on
machines with little memory. More workers do not guarantee shorter runtimes.

Record the passed, failed and skipped totals from the actual run. Explain skips
by surface, such as native PowerShell, an optional framework or a live database.
Do not describe a skipped platform as validated.

## What hosted workflows check

The workflow files are the executable source of truth. They use read-only
repository permissions, pinned action revisions and local image builds. They
do not publish Docker images. Core jobs explicitly use UTF-8 on every OS and
create their test workspace before starting four grouped pytest workers.
Windows then runs a separate native private-ACL smoke check outside the parallel
suite. Its artifact records fixed phases and outcomes without account identifiers
or credential material; a mocked unit-policy check cannot replace that evidence.

| Workflow and job | Trigger and scope | What a pass establishes |
| --- | --- | --- |
| Course validation: Core checks | Push, pull request, manual dispatch and weekly schedule; Linux Python 3.11/3.12, Windows and macOS Python 3.12 | Lock, generated artifacts, content contracts, UI behavior, lint, typing, grouped tests and selected notebook execution on the named runner |
| Course validation: Learner bootstrap | Same triggers; Windows, macOS and Ubuntu | Fresh native setup and diagnostics, without claiming every optional runtime works |
| Course validation: PostgreSQL 17 end-to-end | Same triggers; disposable PostgreSQL service | All cataloged SQL learner/reference sequences, live database tests and the PostgreSQL magic notebook against the course database |
| Course validation: Advanced imports | Manual dispatch and weekly schedule; three OS families | Frozen all-extras installation and isolated imports, without downloading pretrained models or proving full model training |
| Application builds: Portable Docker classroom starter | Push, pull request and manual dispatch | A complete source bundle assembled through the allowlisted packaging path |
| Application builds: Optional native application | Same triggers; Linux, Windows and macOS | A native bundle builds and passes its bundled-asset self-check on that runner |
| Application builds: Docker classroom | Same triggers; isolated Linux groups covering all ordinary profiles | Every admitted ordinary module reference runs in its declared worker; real compiler failures, timeout recovery and saved receipts are checked |
| Application builds: Chromium acceptance | Python Core Docker group, after container replacement | Real browser navigation, isolated pads/results, saved progress, output contrast, mathematical rendering and the three browser JavaScript references work |
| Owned Kubernetes runtime | Manual dispatch and weekly schedule; disposable Linux kind cluster | Every admitted bounded Kubernetes reference and explicit failure/timeout/cancellation cases produce matching receipts and verified owned cleanup |
| Windows runtime diagnostics | Manual dispatch; native Windows Python 3.12 | Controlled PowerShell startup comparisons, real private-file ACL acceptance and focused portal/diagnostic contracts run separately |

The Docker groups cover Python Core, C++, Java, JavaScript/TypeScript,
Scala/Spark, TensorFlow and PyTorch. The Core group runs the statistics book,
NLP and compatible LLM examples once; the framework groups execute their own
TensorFlow, PyTorch and LLM references. PySpark and tutorial example variants
are discovered from the same catalog used by the classroom. There is no second
hand-maintained lesson list. Reading/manual lessons and owned-cluster operations
appear as explicit exclusions from the ordinary corpus, never successful runs.

Each group owns a disposable project. At most two Docker groups run together,
and each worker executes one reference at a time. The corpus records failures,
source hashes, actual exit status and typed checks where registered. An overall
time budget leaves unexecuted cases visibly pending and fails the job. Artifact
JSON distinguishes reference execution from independent typed verification.
Negative probes restore the previous source and notes, and container replacement
checks read the original successful receipts without replay.

Chromium runs only in a separate CI browser environment with hash-locked packages.
It is absent from the production image. Browser reports contain check results and
screenshots, without session credentials or network traces. The separate Kubernetes
workflow prepares checksum-verified host tools and a short-lived owned cluster,
checks all supported reference manifests and cleanup behavior, then releases only
its recorded resources. Optional pretrained-model downloads and external services
remain outside these offline qualification paths.

A Linux hosted Docker result does not establish Windows WSL installation,
macOS engine setup, another CPU architecture, GPU support or every rootless
engine configuration. A native executable self-check does not prove every
lesson's backend. Check the actual matrix architecture and receipt before
making a release claim.

To run the workflows manually, open the repository's **Actions** tab, select
**Course validation**, **Application builds**, **Owned Kubernetes runtime** or
**Windows runtime diagnostics**,
choose **Run workflow**, and
select the revision to validate. With an authenticated GitHub CLI:

```text
gh workflow run ci.yml --ref BRANCH_NAME
gh workflow run app-build.yml --ref BRANCH_NAME
gh workflow run kubernetes.yml --ref BRANCH_NAME
gh workflow run windows-runtime.yml --ref BRANCH_NAME
```

The focused Windows workflow compares fixed startup conditions without changing
machine policy or exposing account identities, environment values or raw native
output. Completing those comparisons establishes diagnostic coverage only. The
separate native ACL smoke must establish a private directory, accept its private
file and reject an intentionally broad file ACL. A startup marker alone cannot
satisfy that check. Later focused tests still run after a diagnostic failure,
while the failed step keeps the workflow unsuccessful.

Read failed job logs and uploaded test results. A workflow syntax check is
useful before pushing, but only a hosted run can establish hosted acceptance.

## Exercise the Docker product on disposable data

Create a new project name that has never held learner work. For example, on
macOS, Linux or Windows through WSL 2:

```bash
./classroom --project ds60-release-check --no-browser
```

Use the exact URL printed by that launcher, or read
`.classroom/ds60-release-check/classroom.url`. The following commands write test
pads and reset the course SQL fixture, so replace `CLASSROOM_URL` only with that
disposable project's loopback URL:

```text
python scripts/check_lab_http.py --url CLASSROOM_URL --confirm-disposable --reset-sql
python scripts/check_classroom_profiles.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python" --report work/release-runtime-receipts.json
```

To run the complete admitted module corpus for selected prepared profiles:

```text
python scripts/check_module_references.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20" --report work/module-reference-results.json
python scripts/check_classroom_failures.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20" --check-timeout --report work/runtime-failures.json
```

The first command executes every selected module reference, including applicable
book examples and variants. The second deliberately submits invalid code and a
real 15-second Python timeout, checks diagnostics and recovery, and restores the
prior source. These commands still need disposable state. `--list-only` on the
corpus checker produces the inventory report without HTTP or execution; omit
`--url` and `--confirm-disposable` in that mode.

The profile checker runs cataloged reference source through the authenticated
classroom and records source-bound results. It does not declare every lesson
execution-verified from one representative program. For changed runtime or
lesson code, also run the relevant full reference corpus and its boundary/failure
cases. Compile errors, runtime errors, timeouts and successful execution must
remain distinct results.

Replace the disposable project's containers while retaining its volumes, then
run both checks in persistence mode against the newly printed URL:

```text
python scripts/check_lab_http.py --url CLASSROOM_URL --confirm-disposable --check-persistence
python scripts/check_classroom_profiles.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python" --report work/release-runtime-receipts.json --check-persistence
```

Persistence verification must read the original receipt rather than rerun code
to recreate the expected result. A saved result belongs to its source, lesson,
language and SQL mode. Receipt-storage failure after successful execution must
not trigger an automatic replay.

After validation, stop only the test project with:

```bash
./classroom stop --project ds60-release-check
```

Removing named volumes is a separate destructive action. Never use a global
volume prune as part of a learner-facing cleanup procedure.

## Browser acceptance

The Python Core Docker job runs `scripts/check_classroom_browser.py` against
its actual classroom after persistence checks. For a prepared Linux x86_64
Python 3.12 browser environment, install `requirements/ci-browser.lock`, install
Chromium with `python -m playwright install --with-deps chromium`, then run:

```text
python scripts/check_classroom_browser.py --url CLASSROOM_URL --confirm-disposable --report work/browser-receipts.json
```

Use `--fixtures-only --report work/browser-fixtures.json` to execute just the
isolated JavaScript browser references. A unit test of the probe's helpers is
not a substitute for this real Chromium run. The browser probe writes its own
disposable pads and progress; do not point it at a learner workspace.

Use a separate browser profile and disposable classroom state for checks that
edit code or notes. Inspect the actual running page at desktop and narrow
widths, in light and dark modes, using keyboard navigation as well as a mouse.

Check these user journeys:

- Open the common home, search for a subject, choose a lesson and switch subjects.
- Follow guide/reference links, render equations and code, and avoid raw source
  pages or broken anchors.
- Edit a Python pad, run it, see readable stdout and a plot, then return after a
  page reload and verify the source, notes and saved result.
- Run both SQL snippet and whole-lesson modes against the disposable database;
  preserve their separate drafts and result histories.
- Compile and run a C++ or Java example and a TypeScript example. Deliberately
  introduce a small compiler error and verify that the diagnostic is truthful.
- Open an older result without replacing the current pad. Switch lessons while
  a result loads and verify that late responses stay in their original context.
- Confirm a reading-only lesson explains its capability and does not advertise
  execution. Tutorial read markers must not imply tested mastery.
- Confirm focus, contrast, navigation labels, mobile layout and local asset
  loading. No runtime CDN should be needed for math or highlighting.

Also inspect `START_HERE.html` as a separate static reading mode. Static browser
progress and server-backed classroom progress have different storage boundaries.
Unit and DOM tests supplement this review; they do not replace it.

## Notebook, SQL and optional-runtime boundaries

`python scripts/validate_notebooks.py` checks structure. Add `--smoke` for the
selected dependency-light execution set. Heavy training, external assets and
SQL magic cells require their own declared environments. Keep executed copies
under ignored `artifacts/`, and keep source notebooks free of incidental output.

Live SQL tests require the exact local disposable `advanced_sql_training`
database. The environment opt-ins are documented in the fixtures and hosted
PostgreSQL job. Never aim reset commands at a production or shared database.
Use `psql -X -v ON_ERROR_STOP=1`; the Day 52 to 54 warehouse sequence is the
explicit stateful exception to otherwise independent rollback-safe lessons.

The optional MCP tests use the actual stdio protocol and read-only defaults.
They verify discovery, bounded content reads, explicit solution reveal and
opt-in progress behavior. They do not call a hosted model or measure teaching
quality. See [MCP tutoring](mcp-tutor.md).

Compiler/framework reference tests must identify the prepared profile, actual
source and observed result. A Dockerfile, installed dependency, parse-only
check or old image hash is not current execution evidence. Preserve truthful
historical receipts, but attach fresh evidence when executable source changes.

## Release decision

Before shipping, record the exact revision, generation drift result, quality
checks, test totals and skipped surfaces, runtime receipts, browser observations,
archive contents and supported-platform evidence. Verify no learner state or
private configuration entered the package. Explain unresolved failures before
publishing; do not rename them as expected skips.

Useful result labels are **structure validated**, **representative behavior
executed**, **complete artifact executed**, **offline verified after setup**,
and **not validated on this platform**. Use the narrowest label supported by
the evidence. No finite test suite establishes that software has no bugs.
