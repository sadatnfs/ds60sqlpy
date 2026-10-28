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

The supported product is the Linux-container Docker classroom. Windows runs
through WSL 2; macOS uses its engine's Linux environment. Native Windows
backends and native executable bundles are outside the release support matrix.

Maintainers running contributor checks on Linux or WSL 2 also need
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
inside this checkout's `.venv`. On Windows, WSL 2 provides the same Bash, Linux
Python environment and Docker workflow. Retired native installers and executable
builders are no longer shipped; they are not alternate release requirements.

Core setup does not install every heavy learning dependency. A test that needs
an optional compiler, framework, SQL service or model asset must either run in
its prepared environment or report that boundary explicitly.

## Repository formatting

Run `./scripts/format-repo` to apply maintained code style, or
`./scripts/format-repo --check` to report drift without editing tracked source.
Make exposes the same commands as `make format` and `make format-check`.
`./scripts/lint-repo` (or `make lint`) adds read-only static source checks using
the same toolchain. `make check` requires both formatting and lint checks.
These commands use pinned Docker toolchains on Linux, macOS and Windows
through WSL 2. R uses its compatible styler/lintr image and Julia uses its
prepared JuliaFormatter/parse tool image. Other languages use the main image,
including stanc for Stan and SQLfmt for dbt SQL/Jinja. A full pass runs the
separate adapters before refreshing shared generated views after successful
source formatting. Image fingerprints follow tool inputs rather than lesson edits.
The first invocation prepares missing images; `--build` explicitly rebuilds them,
and `--list` reports coverage without formatting source. Classroom containers
and learner volumes are not part of this operation.

The R adapter parses without evaluating lesson code and checks that formatting
preserves parsed expressions. Its fixed lexical lint rules do not substitute for
runtime assertions. Check and lint modes use read-only source mounts. A focused
language pass omits shared regeneration, so finish with the unfiltered checks.

Use a repeated `--language` selection for focused iteration and the unfiltered
check before submission. Follow [the contributor formatting workflow](../CONTRIBUTING.md#format-the-repository)
for generated-source ownership and optional pre-commit installation. Formatting
checks and execution checks are separate evidence: still compile/run changed
examples and inspect lesson rendering when either may be affected.

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
python scripts/compile_lesson_tex.py --check
python scripts/build_lesson_readers.py --check
python scripts/check_modules.py
python scripts/check_repository_guidance.py
python scripts/validate_notebooks.py
node scripts/check_classroom_ui.mjs
python -m ruff check src scripts tests bridge python/professional docker/init_module_runtime.py
./scripts/format-repo --check
./scripts/lint-repo
python -m mypy
python scripts/scan_secrets.py --history
git diff --check
```

`normalize_lesson_prose.py` is a dry check by default. When deliberately
refreshing reviewed prose, run it with `--write` after authoring generators and
before HTML generation. `check_content_rendering.py` renders the actual
published Markdown and notebooks, checking mathematics and code blocks through
the production reader. A generic Markdown parser is not a substitute.

`compile_lesson_tex.py --check` recompiles explicit TeX with the pinned bundled
KaTeX compiler and checks the input inventory, compiled HTML/MathML and integrity
binding. Node is needed for this contributor check; no runtime CDN is used.
Intentional generation normalizes prose, compiles TeX and then builds readers.
`--check-inputs` checks source coverage and cache integrity without invoking Node;
it does not recompile. A successful compiler check establishes supported syntax
and synchronized typesetting artifacts, not correct derivations or statistical
assumptions. Code remains literal, and uncompiled draft expressions retain the
safe native MathML fallback.

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
by surface, such as an optional framework, a live database or historical
optional services or platform-specific filesystem cases.
Do not describe a skipped platform as validated.

## What hosted workflows check

The workflow files are the executable source of truth. Routine validation uses
read-only repository permissions, pinned action revisions and local image builds.
The separate [image publication workflow](dockerhub.md) opts in only on a push
to `main` with `[publish-docker]` in the HEAD message. It uses the two repository
secrets, builds/qualifies native AMD64 and ARM64 groups, uploads commit-specific
staging images and small receipts, then promotes combined version/latest tags
only after all required checks. It requires no extra enable variable or protected
environment. Staging uploads are not a completed release; conflicting source
versions are refused rather than overwritten.

Linux core jobs use UTF-8 and create their test workspace before starting
four grouped pytest workers. Native Windows ACLs,
PowerShell backend diagnostics and native executable bundles are not release
gates. Windows Docker wrappers remain supported entrypoints into WSL 2.

| Workflow and job | Trigger and scope | What a pass establishes |
| --- | --- | --- |
| Course validation: Source formatting and lint | Push, pull request, manual dispatch and weekly schedule; separate main/R/Julia Linux Docker jobs | The pinned formatter finds no maintained-source or owned generated-view drift; scoped static and syntax checks pass, leaving the checkout unchanged |
| Course validation: Core checks | Push, pull request, manual dispatch and weekly schedule; Ubuntu Python 3.11/3.12 | Lock, generated artifacts, content contracts, UI behavior, lint, typing, grouped tests and selected notebook execution |
| Course validation: Contributor bootstrap | Same triggers; Ubuntu Python 3.12 | Fresh Linux contributor environment and diagnostics, also used by the WSL development route |
| Course validation: PostgreSQL 17 end-to-end | Same triggers; disposable Linux PostgreSQL service | All cataloged SQL learner/reference sequences, live database tests and the PostgreSQL magic notebook against the course database |
| Course validation: Advanced imports | Manual dispatch and weekly schedule; Ubuntu Python 3.12 | Frozen all-extras installation and isolated imports, without downloading pretrained models or proving full model training |
| Application builds: Portable Docker classroom starter | Push, pull request and manual dispatch; Ubuntu | A complete source ZIP assembled through the allowlisted packaging path for Docker/WSL learners |
| Image publication | Push to main with `[publish-docker]` in HEAD | Native AMD64/ARM64 qualification and source/digest-bound promotion; staging images are distinct from completed version/latest tags |
| Application builds: Docker classroom | Push, pull request and manual dispatch, except marked main publication pushes; isolated Linux groups cover all ordinary profiles | Every admitted ordinary module reference runs in its declared worker; real compiler failures, timeout recovery and saved receipts are checked |
| Application builds: Scientific figures | Python Core and R Docker groups, before and after container replacement | Declared source-bound figures are captured, original drafts are restored, and the original figure receipts survive replacement without replay |
| Application builds: Chromium acceptance | Python Core Docker group, with container replacement checks | Real browser navigation, isolated pads/results, saved progress, contrast, typeset mathematics, web live previews, all 24 D3 references, all eight Plotly variants and the offline DAX editor/reference flow pass their stated checks |
| Owned Kubernetes runtime | Manual dispatch and weekly schedule; disposable Linux kind cluster | Every admitted bounded Kubernetes reference and explicit failure/timeout/cancellation cases produce matching receipts and verified owned cleanup |

A marked main publication push keeps source validation and the starter ZIP
mandatory, then uses the publication workflow's native AMD64/ARM64 seed and
worker groups instead of duplicating the ordinary Docker matrix. The publisher
waits for the exact revision's required source/starter success and rechecks it
before promotion. Successful same-run/revision receipts can be reused across
failed-job retries with exact seed-digest binding; cross-run reuse is rejected.

The Docker groups cover Python Core, C, C++, Go, C#, Rust, Swift, Java,
JavaScript/TypeScript, PHP, Scala/Spark, TensorFlow, PyTorch, JAX CPU, Bayesian CPU,
R, data engineering, Apache data-platform libraries, dbt/DuckDB, Stan and Julia.
Their separately prepared worker images preserve incompatible dependency and
compiler contracts.
The Core group runs compatible statistics-book, NLP and LLM examples; dedicated
groups execute references requiring their own frameworks. Representative smoke
cases establish only their selected behaviors;
the catalog-driven corpus separately executes every admitted reference in each
selected profile. Bounded Bayesian diagnostics remain evidence to interpret,
not a declaration of convergence. PySpark and tutorial example variants
are discovered from the same catalog used by the classroom. There is no second
hand-maintained executable lesson list. Reading/manual lessons, offline DAX and
owned-cluster operations appear as explicit exclusions from the ordinary corpus,
never successful ordinary-worker runs. DAX has no execution engine or compiler
requirement; its saved editing and hand-derived comparison flow is browser-tested.
CUDA CPU models and the selected CPU framework/Spark variants run in those ordinary
groups. Optional NVIDIA profiles remain explicitly excluded: CPU execution,
compiler-only acceptance and GPU device execution require separate receipts.

Each group owns a disposable project. At most four Docker groups run together.
One classroom controller admits one active module job across all profiles, so
parallel runtime qualification requires separate disposable projects. The grouped
unit suite independently supports four workers. The corpus records failures,
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
its recorded resources. The owned project gates below qualify selected local
services separately from the ordinary reference corpus. Optional pretrained-model
downloads and other external environments retain their explicit preparation
and qualification boundaries.

A Linux hosted Docker result does not establish Windows WSL installation,
macOS engine setup, another CPU architecture, GPU support or every rootless
engine configuration. Check the actual matrix architecture and receipt before
making a release claim. Historical native-platform results do not add supported
product targets or create release requirements.

To run the workflows manually, open the repository's **Actions** tab, select
**Course validation**, **Application builds** or **Owned Kubernetes runtime**,
choose **Run workflow**, and select the revision to validate. With an
authenticated GitHub CLI:

```text
gh workflow run ci.yml --ref BRANCH_NAME
gh workflow run app-build.yml --ref BRANCH_NAME
gh workflow run kubernetes.yml --ref BRANCH_NAME
```

The manual Course validation run includes the Linux advanced-imports job.
Keep its evidence attached to the same revision as the Docker and source-ZIP
checks. Repository settings can disable workflows for private fork pull
requests; a `pull_request` trigger does not override that access policy.

Read failed job logs and uploaded test results. A workflow syntax check is
useful before pushing, but only a hosted run can establish hosted acceptance.

## Optional documentation-only CI skip

For a push containing only prose and its regenerated readers, the native
`[skip ci]` commit-message token skips `push` and `pull_request` workflows.
Use the space; `[skip-ci]` is not a supported native token. No YAML gate or
custom alias is required. Follow [the commit example and push boundary](../CONTRIBUTING.md#optional-ci-skip-for-a-prose-only-push).

Before that commit, use the prepared contributor environment to regenerate and
check the documentation locally:

```sh
make generate
python scripts/normalize_lesson_prose.py
python scripts/check_content_rendering.py
python scripts/check_published_links.py
git diff --check
```

Review the whole push: executable lesson examples, tests, runtime code,
configuration, dependencies and workflows require normal CI. Never hide an
unvalidated implementation commit behind a marked documentation commit.
Scheduled/manual runs are unaffected; existing runs are not cancelled. Required
PR checks may remain Pending and prevent merging. Trigger normal checks with
an unmarked follow-up commit, or use a manual run only if the repository's
required-check policy accepts it. A skipped run is not passing CI evidence.
[GitHub documents the event and required-check behavior](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).

## Exercise the Docker product on disposable data

Create a new project name that has never held learner work. For example, on
macOS, Linux or Windows through WSL 2:

```bash
./classroom --rebuild --all --project ds60-release-check --no-browser
```

The explicit `--rebuild` qualifies current source rather than silently resuming
an older image with the same tag. `--all` selects the full ordinary worker set
even if this disposable project previously saved a smaller selection. For a
focused check, replace `--all` with the required `--profile` options. Source
updates do not take effect merely because a default resume succeeds.

Use the exact URL printed by that launcher, or read
`.classroom/ds60-release-check/classroom.url`. The following commands write test
pads and reset the course SQL fixture, so replace `CLASSROOM_URL` only with that
disposable project's loopback URL:

```text
python scripts/check_lab_http.py --url CLASSROOM_URL --confirm-disposable --reset-sql
python scripts/check_classroom_profiles.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python c17 go csharp-dotnet rust-stable swift-linux php-cli jax-cpu bayesian-cpu r-statistics data-engineering data-platforms-python dbt-duckdb stan-cpu julia" --report work/release-runtime-receipts.json
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

For selected prepared Python Core and R profiles, also capture the declared
scientific figure references before replacing containers:

```text
python scripts/check_scientific_artifacts.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core r-statistics" --report work/scientific-artifact-receipts.json
```

Select only profiles prepared in this disposable project. The explicit reviewed
inventory covers Python `viz-001` through `viz-008` and R `r-051` through `r-060`.
This existing visualization/R gate remains separate from per-subject
`figure-contracts.json` checks in the full module corpus. The corpus validates
new scientific tables, JSON reports and chart requirements through
`scripts/declared_outputs.py`. Both require actual output; a declaration alone
is not evidence. The visualization/R gate binds source hashes, figure kinds/counts
and required accessible Plotly metadata,
and checks complete PNG chunks and checksums. A computation that succeeds while
losing its expected figures fails this gate. Reference edits require deliberate
review of the expectations and source digests. The gate restores prior drafts
and notes after each run; it does not infer that every R lesson produces a plot.

Replace the disposable project's containers while retaining its volumes, then
run the applicable checks in persistence mode against the newly printed URL:

```text
python scripts/check_lab_http.py --url CLASSROOM_URL --confirm-disposable --check-persistence
python scripts/check_classroom_profiles.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python c17 go csharp-dotnet rust-stable swift-linux php-cli jax-cpu bayesian-cpu r-statistics data-engineering data-platforms-python dbt-duckdb stan-cpu julia" --report work/release-runtime-receipts.json --check-persistence
```

If scientific figures were captured, read those original receipts as well:

```text
python scripts/check_scientific_artifacts.py --url CLASSROOM_URL --confirm-disposable --profiles "python-core r-statistics" --report work/scientific-artifact-receipts.json --check-persistence
```

This compares original job identities, source/output/figure hashes and restored
saved pads without execution or writes. Run it before later acceptance scenarios
deliberately edit the same lesson drafts, or use a separate disposable project.
A second read against an unchanged process does not prove replacement durability.

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

The web-development checks exercise all 30 HTML reference pages, real script
lifecycle and module behavior, opaque-origin isolation, HTML/CSS and browser
JavaScript/D3 live updates, viewport controls, focus, pause/stop and explicit
observation saving:

```sh
python courses/web-development/authoring/check_browser.py --url CLASSROOM_URL --confirm-disposable --report work/web-browser-receipts.json
python courses/web-development/authoring/check_live_preview.py --url CLASSROOM_URL --confirm-disposable --report work/live-preview-receipts.json
```

Run them before the full D3 checker because both use some D3 lesson workspaces.
Automatic preview updates must create no saved-run receipts. A manual run or
explicit observation save records the exact submitted source. These client
observations are not independent server verification. The separate
[PHP HTTP fixture](../courses/web-development/fixtures/php-http-lab/README.md)
qualifies cookies, sessions, CSRF handling and persistence through real requests;
PHP CLI success alone does not establish those behaviors.

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

Run the paired Plotly and offline DAX gate in the prepared browser environment:

```text
python scripts/check_plotly_browser.py --url CLASSROOM_URL --confirm-disposable --report work/plotly-browser-receipts.json
```

All eight JavaScript variants are exercised through the real classroom pad and
Run control. The checks cover SVG output, declared source-table row counts,
keyboard filters, figure JSON export, narrow layouts and no external requests.
Original drafts and notes are restored. DAX001 separately checks source save,
reload and exact export, hand-derived reference comparison without replacing the
draft, hidden execution controls, the keyboard no-run guard and mobile layout.
It does not execute DAX or require Power BI, an account or an external service.

After replacing the same disposable project's containers while retaining volumes,
use the newly printed URL and the original report:

```text
python scripts/check_plotly_browser.py --url CLASSROOM_URL --confirm-disposable --report work/plotly-browser-receipts.json --check-persistence
```

This mode reads original Plotly observation IDs, restored source/note hashes and
DAX source/model reference bindings without launching a browser or submitting
execution. Retain the report from both phases. Plotly browser records remain
client observations with `verified: false`, not independent worker verification.
The workflow supplies the actual replacement boundary; the checker cannot infer
that replacement occurred merely because its reads succeeded.

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

A guide may have a separate binding in `curriculum/presentation-parity.json`.
For a prose-only correction, first verify that the committed guide matches the
previous presentation hash and that every protected code block still matches
its recorded hash. Preserve the historical runtime hash and code hashes. Record
the previous and updated presentation hashes, baseline commit and reason in the
binding's `presentation_history`, then update its current presentation hash and
run the existing parity tests. This records a documentation change, not another
execution. Never use it to approve changed examples or rewrite runtime receipts.

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

## D3 and new systems-language qualification

The ordinary reference corpus discovers C17, Go, C#, Rust and Swift programs
from their manifests and runs them in their packaged Linux workers. The profile
smoke gate uses an actual catalog reference and its observed completion marker;
the failure gate requires the real staged filename and compiler diagnostic.
Rust Arrow dependencies are prepared in the image. Ad hoc Cargo, NuGet or Go
module downloads are not part of a lesson Run. Swift Apple UI projects remain
explicitly outside the Linux compiler contract.

D3 uses a separate browser runtime and is excluded from ordinary worker corpus
execution. In the prepared browser environment, run:

```sh
python scripts/check_d3_browser.py --url CLASSROOM_URL --confirm-disposable --report work/d3-browser-receipts.json
```

The checker submits all 24 references through the real classroom pad and Run
button. It verifies chart output, source-bound saved client observations,
keyboard controls, actual pointer brushing and wheel zoom, filtering, fresh
browser-session persistence, history without rerun, failure/recovery, opaque
origin/CSP isolation and stale-frame navigation. These results remain browser
observations with `verified: false`, no process return code and no worker checks.
The checker does not relabel browser output as independent server verification.
The Python Core Docker CI group executes it after container replacement.

The Docker study subject is reading/manual practice. Its optional fixture uses
an explicitly owned host project; it never mounts the engine socket into the
classroom. Deep Kubernetes networking fixtures are also reading/manual unless
the exact advanced capability was separately prepared and qualified. Run
`python courses/kubernetes/fixtures/networking/check_fixtures.py` for offline
consistency only. An offline pass does not prove NetworkPolicy enforcement,
load-balancer provisioning, Gateway routing or dual-stack traffic.

After the D3 execution report is complete, replace the same disposable Core
project's containers while retaining volumes, then use the newly printed URL:

```sh
python scripts/check_d3_browser.py --url CLASSROOM_URL --confirm-disposable --report work/d3-browser-receipts.json --check-persistence
```

This phase reads the original observation IDs and compares complete-record,
source and output hashes, plus the final saved source/note hashes for every D3
lesson. It does not launch a browser, rerun code or write learner state. The
report retains the original execution evidence and appends the readback result.
The invoker must actually perform container replacement; a second read against
the same process alone does not prove replacement durability. The Python Core
CI job supplies that explicit down/up boundary after its D3 run.

## Guidance and retirement checks

`python scripts/check_repository_guidance.py` checks maintained documentation,
AGENTS files and both repository skills without network access or source writes.
It resolves local Markdown targets, verifies loader-derived subject README/AGENTS
coverage and skill identities/references, rejects checkout escapes, and catches
retired command paths in guidance. Use `--json` for machine-readable output or
`--report PATH` for an explicit report. Code literals are not treated as document links;
fragment IDs remain the responsibility of the published HTML link checker.

The gate runs in Course validation, `make check` and the source-starter builder.
A clean report does not establish pedagogical quality or prove every source file
is used. Review changed workflows and run the relevant behavioral tests as well.
Preserve immutable execution receipts and course source/solution separation when
retiring a feature. Remove its entrypoints, callers, tests and documentation together;
keep shared security or persistence behavior until its replacement is qualified.

## Scientific and data-system release gates

Use the subject's own authoring check, independent numerical tests and complete
reference corpus. Applied Science, Bayesian Computing, Julia and LLM evaluation
have documented `authoring/build.py --check` commands. Polars, dbt and ML
engineering have their own source/check contracts. Read those authoring guides
instead of applying one generator to every subject.

Prepare only the necessary profiles in an explicitly disposable classroom,
then run their real references through the normal HTTP/job path:

```text
python scripts/check_module_references.py --url CLASSROOM_URL --confirm-disposable --profiles "data-engineering dbt-duckdb stan-cpu julia" --report work/scientific-runtime-references.json
```

The declared output check requires kind/count and any specified descriptions or
table rows. Exercise source-bound JSON/table display, download, dark/light
contrast, narrow layouts, history and container replacement in the browser as
well. Preserve exact large integer identifiers as strings. Test output-storage
failures separately from computation failures, and verify that neither a
successful computation nor an actual failed build is relabeled by a secondary
publication error.

For Stan, qualify actual translation, compilation, bounded sampling, diagnostics
and captured trace/table output. Run the separate normal-mean project with its
real `data.json` and explicit output directory. A passing syntax check or tiny
chain does not establish convergence. For Julia, inspect all runnable references
and complete worked programs with the prepared project/depot; static parse checks
must not evaluate the source. For dbt, test both SQL-model variants and complete
project configuration, including actual failed data tests and recovery.

The [owned ML service checker](../courses/ml-engineering/projects/local-system/README.md#reproduce-the-release-checks)
uses a new project and explicit `--confirm-disposable`. It exercises real
training, HTTP prediction, model activation/rollback, freshness, integrity and
container replacement. Its state is separate from classroom learning volumes.
Keep those service results separate from ordinary pad references and hosted CI.
Do not infer cloud security, production scale or another CPU architecture from
a local fixture. Record images, source hashes, platform, actual checks, skips and
remaining limits; workflow configuration is not a hosted success report.

## Owned engineering and platform project gates

The ordinary pad corpus and a persistent service answer different questions.
[`scripts/ci_classroom.py`](../scripts/ci_classroom.py) requires the following
owned checks in addition to each native group's source-bound references,
compiler/error probes and classroom persistence gates:

| Native Docker group | Additional required behavior | Maintained entrypoint |
| --- | --- | --- |
| `data-engineering` | Real ML training/HTTP, model activation and rollback | [ML service lifecycle checker](../courses/ml-engineering/projects/local-system/README.md#reproduce-the-release-checks) |
| `data-engineering` | Real ingestion HTTP, exact replay/conflicts, immutable Parquet publication, controlled process failure, recovery and rollback | [Data-product checker](../courses/data-ml-engineering/projects/data-product/README.md) |
| `pytorch` | Actual tiny-model generation, queue/cancellation, SSE, Chromium, exact-container resume and retained request history after replacement | [Inference project checker](../courses/data-ml-engineering/projects/inference-service/README.md#maintainer-lifecycle-gate) |
| `data-platforms` | Actual Flight RPC and compiled Rust/Python IPC, error cases and retained data | [Arrow Flight workshop](../courses/apache-data-platforms/projects/arrow-flight/README.md) through the common workshop qualifier |
| `java` | Actual Kafka records, transactions, offsets, consumers and compaction-safe retained state | [Kafka workshop](../courses/apache-data-platforms/projects/streaming/README.md) through the common workshop qualifier |

The common qualifier is
[`courses/apache-data-platforms/authoring/qualify_workshop.py`](../courses/apache-data-platforms/authoring/qualify_workshop.py).
Read its `--help` and each project's instructions before use. It requires fresh
workspaces/evidence paths and explicit prepared image selections. Its Kafka
`--prepare` route deliberately downloads and verifies the official distribution;
this is preparation, not an offline lesson Run. The Flight gate's `--require-ipc`
requires the actual compiled cross-language path. Heavy service projects should
be prepared sequentially when engine disk or memory is constrained.

The data-product and inference checkers require `--confirm-disposable` and
already prepared native images. Their project READMEs provide copy-ready commands.
Inference browser qualification additionally needs an explicitly prepared
Playwright interpreter; the native CI gate requires it. Learners use the
project's Bash/Docker launcher and their ordinary browser, without installing
those contributor check dependencies.

Every gate records actual source, image and native platform identities. Preserve
original successful receipts and verify readback without repeating completed
operations. Cleanup is limited to resources created for that check; private
project state and evidence are distinct from classroom learning volumes.

Other platform projects have their own supported operation and failure scopes.
Consult the [current qualification ledger](../courses/apache-data-platforms/authoring/ENVIRONMENTS.md)
and project-specific checks. Prepared Atlas/Delta Sharing clients are not live
server acceptance. A successfully checked component does not qualify an
unexecuted combined topology, a different CPU architecture or a GPU runtime.
The workflow definition and local reports do not prove that hosted jobs ran.

## Scientific classroom browser acceptance

Use an explicitly disposable classroom prepared with `python-core`,
`data-engineering`, `dbt-duckdb`, `stan-cpu` and `julia`. The maintained browser
checker verifies the shared subject directory and tutorial interface, actual
Polars/dbt/Julia/Stan execution, compiler diagnostics, structured result rendering,
exact downloads, offline behavior and distinct source/history state. It runs jobs
sequentially because each classroom has one active-job controller.

In the isolated Playwright contributor environment described above:

```sh
python scripts/check_scientist_browser.py --url "$CLASSROOM_URL" \
  --confirm-disposable --report work/scientist-browser.json
```

Use `--profiles python-core dbt-duckdb` to qualify only those prepared runtime
probes. A subset still checks the complete directory but does not establish
execution for omitted profiles. After replacing this same disposable project's
containers while retaining its named volumes, use its current URL and the same
profile selection:

```sh
python scripts/check_scientist_browser.py --url "$CLASSROOM_URL" \
  --confirm-disposable --report work/scientist-browser.json --check-persistence
```

The second command uses the original receipt IDs and fresh browser documents;
its request guard rejects writes and execution. Keep the report from the first
run. Changing a report, rerunning code or selecting another project does not
prove persistence. The checker restores the prior effective pads after its
initial probes and does not mark learner completion.
