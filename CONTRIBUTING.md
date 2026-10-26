# Contributing

Help make DS60 accurate, teachable and reproducible. Small fixes are welcome.
A curriculum change should keep its guide, learner artifact, reference,
metadata and rendered pages consistent. A runtime change needs evidence from
execution, including failure behavior, rather than only a successful build.

## Choose your setup

To learn or inspect the running product, install a Linux-container engine with
Compose and run `./classroom`. Windows uses WSL 2. The
[one-command guide](docs/one-command-classroom.md) covers installation, logs,
profiles, storage and recovery. No host language toolchain is needed for the
ordinary Docker route. The supported delivery target is Linux containers.
Windows contributors use the WSL 2 Linux environment. The product has one
classroom UI; native executable installers and editor-launch services are retired.

For application development or content generation, use Python 3.12 and the
checked-in dependency lock. From the repository root, with `uv` installed:

```sh
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks
uv run --no-sync python scripts/course.py validate
uv run --no-sync python scripts/check_modules.py
```

Run these commands in Linux or WSL 2. `uv run --no-sync` uses the prepared
environment without activating it. Node.js is needed for the UI behavior
checker, with Node.js 24 used by CI. Optional framework and compiler checks use
their declared container profiles; do not install every large dependency for an
unrelated docs edit. The optional repository Serena configuration indexes the
maintenance sources; it does not require host SDKs for every taught language.
See [dependency profiles](docs/dependency-profiles.md) and
[validation](docs/validation.md).

For a contributor-only loopback server using this same prepared Python environment:

```sh
uv run --no-sync python scripts/course.py serve --no-browser
```

The installed equivalent is `ds60 serve`. Use `--port PORT` to choose a port;
`--python PATH` explicitly selects the interpreter for supported local execution.
Put the global `--repo PATH` option before `serve` when selecting a checkout.
This serves the unified classroom and reports actual local/worker capabilities.
It does not prepare Docker workers or import a Docker volume's learner state.
Use a disposable local workspace for browser and persistence tests. For ordinary
learning and release qualification, use `./classroom` and its prepared workers.

## Before editing

Run `git status --short --branch`, preserve unrelated work, and read
[AGENTS.md](AGENTS.md) plus the closest subject `AGENTS.md`. Do not overwrite
learner files or commit `.learning/`, `.classroom/`, credentials, caches or local
logs. Use UTF-8, repository-relative paths and the checked-in editor settings.

Find the durable source before changing a generated artifact:

| Work                         | Start here                                                                                                             |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Python, SQL or bridge lesson | Subject `AGENTS.md`, catalog builder and lesson artifacts                                                              |
| New module or language       | [Extension playbook](docs/curriculum-extension-playbook.md), [module contract](docs/implementation/ADDING_A_MODULE.md) |
| Existing generated subject   | Its `courses/<subject>/authoring/README.md`                                                                            |
| Browser interface            | `src/ds60sqlpy/assets/classroom.*` and `classroom.py`                                                                  |
| Runtime adapter              | `module_jobs.py`, `worker_operations.py`, profile Dockerfile and Compose                                               |
| Reader formatting            | `lesson_reader.py`, `reader_math.py`, `reader_content.py` |
| Source archive and workspace staging | `course_paths.py`, `scripts/course_payload.py`, `scripts/build_starter.py` |
| Image selection/distribution | `docker/classroom-images.tsv`, `scripts/classroom_images.sh`, [Docker Hub](docs/dockerhub.md) |

Python implementation filenames are under `src/ds60sqlpy/`. The repository
[add-learning-path skill](.agents/skills/add-learning-path/SKILL.md) provides a
focused workflow for contributor agents. The
[learning skill](.agents/skills/guide-ds60sqlpy-learning/SKILL.md) is for tutoring.

## Choose a public commit identity

Before committing, review the intended author and committer identity locally.
The repository owner's policy is to omit an email address from new commits.
Configure this repository only, retaining your chosen public name:

```sh
git config --local user.name "Your public name"
git config --local user.email ""
git config --local user.useConfigOnly true
```

Git records an empty email field for this policy. It does not remove the public
name or commit contents. Other contributors may deliberately choose their own
GitHub no-reply identity instead; obtain that exact address from their account
settings rather than inventing one. Do not restore a personal or workplace email
from global configuration or an environment override. Review the resulting
author and committer fields before an authorized push.

These settings apply to future commits. Cleaning tracked files or building a
sanitized source ZIP does not remove names, emails or private content from
existing Git history. History changes affect commit identities and shared
branches, so they require a separate, explicitly authorized maintainer workflow.
Keep committing, history editing and publication under the repository owner's
control. Do not change global Git configuration as part of project setup.

## Write useful learning material

Define the problem, prerequisites and observable outcome. Explain vocabulary
and syntax before using them. Include at least two focused worked examples,
expected observations, common-error diagnosis and next steps. Practice should
progress through prediction, modification, independent work, debugging and
transfer, with separate explanatory solutions. Copying an answer or running a
reference does not establish understanding.

The [content contract](docs/content-authoring.md) specifies the detailed rules.
Legacy lessons retain immutable practice baselines; modules use their subject
contracts. The statistics/ML tutorial deliberately has worked theory and code
without exams, problem sets or hidden solutions. Do not impose practice rules
on that book.

Keep default examples small, deterministic and offline after preparation.
Disclose optional models, datasets, networks, hardware and services. Cite sources
and preserve required licenses. Use original explanations and public or synthetic
fixtures, without workplace identifiers, private infrastructure or machine paths.
Use explicit LaTeX for mathematics and tagged code fences for program examples.
Compile the math with `python scripts/compile_lesson_tex.py` before building
readers. The Docker build uses its own Node compiler stage; contributors running
shared generation directly need Node as well as the prepared Python environment.
Never modify executable logic only to repair typography.

## Format the repository

Use the same formatter entrypoint on Linux, macOS and Windows through WSL 2.
Start your Linux-container engine, then run from the repository root:

```sh
./scripts/format-repo
./scripts/format-repo --check
./scripts/lint-repo
```

The first command applies the maintained formatting rules. The second reports
drift and exits unsuccessfully when changes are needed, without modifying
tracked source files. `make format` and `make format-check` are equivalent.
`make lint` runs the shared static checks. `make check` includes both formatting
and linting before its other source gates.
The formatter builds its dedicated tool image on first use, with visible build
logs, then reuses the local image. Use `./scripts/format-repo --build` after
changing the toolchain or when deliberately rebuilding that image. It does not
rebuild or restart classroom services or change their saved volumes.
If the default npm registry is unreachable during tool-image preparation, set
`DS60_FORMAT_NPM_REGISTRY` to a public HTTPS registry mirror for that build:

```sh
DS60_FORMAT_NPM_REGISTRY=https://registry.yarnpkg.com ./scripts/format-repo --build
```

Package integrity remains checked against the lockfile. The override accepts no
embedded credentials or query parameters and applies only while building tools;
formatting and lint checks themselves run without network access.

Use `./scripts/format-repo --list` to inspect the actual coverage and
`./scripts/format-repo --language python` to narrow an iteration. Repeat
`--language` for several adapters. The unfiltered check is the submission gate;
a language-specific pass is only evidence for that selection. The checked-in
formatter configuration and `docker/formatting/` toolchain own the rules and
versions, so local checks and the single Linux CI source-quality job agree.

Linting uses the same image and leaves repository source read-only. Its output
identifies each check and its coverage. Python implementation lint, shell/static
checks and language syntax checks answer different questions; parser success is
not compilation, runtime behavior or proof of lesson correctness. Keep the
relevant tests and prepared-worker execution checks after linting. A new
language needs a deliberate lint/validation adapter alongside its formatter.

Markdown files are not passed through Prettier. Bare technical identifiers,
inline code and ordinary teaching fences keep their authored spelling and
spacing. Reviewed prose/math normalization and the explicitly owned statistics
example synchronization below are separate steps.

Formatting includes application code, notebooks, every supported language's
executable lesson files, fixtures and authoring programs. Generated executable
programs receive the same style pass as handwritten code; their generators
remain the durable content source. Markdown code fences and literal tutorial
program strings retain their authored text, so source-pairing checks compare
syntax while preserving literal values. Generated HTML, third-party bundles,
dependency locks, immutable runtime evidence and learner state retain their
existing owners. The checked-in policy and `--list` make exclusions inspectable.

Historical worker receipts remain unchanged. For the Python references bound to
those receipts, `curriculum/source-format-parity.json` retains compressed
original bytes, both source hashes and independently checked AST equality.
This records formatting equivalence, not a new successful execution. Future
behavior changes still require fresh runtime evidence. Canonical regeneration
checks apply the pinned formatter before comparing executable output bytes.

For generated subjects, edit the durable authoring source and run that subject's
generator first. Then format the resulting maintained source and refresh the
shared generated views. The full formatting entrypoint coordinates its owned
generated views; subject-specific prose generation remains a separate authoring
step. Review both source and generated diffs, then run relevant runtime and
content checks. Never manually reformat generated HTML to conceal source drift.

The optional `.pre-commit-config.yaml` runs the same Docker formatting and static
checks alongside the sensitive-content scan. Install pre-commit in
your contributor environment, then run `pre-commit install` if you want those
checks before each commit. The engine must be available when the hook runs.
It checks the full working tree, so finish unrelated formatting work and review
the intended changes before committing. Hooks report drift; apply formatting
explicitly and review the diff before staging it.

## Regenerate and validate

Run the relevant subject authoring command first when one exists. Then refresh
shared metadata and readers through Make or the equivalent individual commands:

```sh
make generate
```

`make generate` normalizes reviewed prose, rebuilds the legacy catalog and
reports, and generates the static dashboard and readers. It does not rerun all
subject authoring pipelines. Never hand-edit generated HTML. Review generated
diffs alongside source changes and run the `--check` forms documented in
[validation](docs/validation.md).

Use focused tests while iterating. The full suite uses four grouped workers:

```sh
uv run --no-sync python -m pytest -n 4 --dist loadgroup
```

Keep `--dist loadgroup`: live PostgreSQL tests share a disposable database and
must remain in one scheduling group. Use `-n 0` for serial debugging or fewer
workers on a constrained machine. Optional runtime skips are not successful
runtime tests. Report which toolchains and databases actually ran.

Common publication gates are:

```sh
uv run --no-sync python scripts/check_modules.py
uv run --no-sync python scripts/normalize_lesson_prose.py
uv run --no-sync python scripts/check_content_rendering.py
uv run --no-sync python scripts/course.py validate
uv run --no-sync python scripts/audit_practice.py
uv run --no-sync python scripts/audit_lesson_depth.py
uv run --no-sync python scripts/build_course_guide.py --check
uv run --no-sync python scripts/build_lesson_readers.py --check
uv run --no-sync python scripts/check_published_links.py
uv run --no-sync python -m ruff check src scripts tests bridge python/professional docker/init_module_runtime.py
./scripts/format-repo --check
./scripts/lint-repo
uv run --no-sync python -m mypy
uv run --no-sync python scripts/scan_secrets.py --history
uv run --no-sync python scripts/check_public_release.py
node scripts/check_classroom_ui.mjs
git diff --check
```

A UI change also needs browser checks: subject switching, keyboard navigation,
small screens, both appearances, code/output contrast, math rendering and
saved-work restoration. A runtime change needs the actual prepared worker,
compile or execution errors, cancellation, bounded output and retained drafts.
Only use disposable project resources. Preserve learner volumes during cleanup.
Release CI checks Ubuntu Python 3.11/3.12, Linux contributor setup, PostgreSQL,
Linux-container runtimes and Chromium, the owned Linux Kubernetes adapter and
the portable source ZIP. Scheduled/manual advanced imports also run on Linux.
Optional GPU and cluster profiles have separate capability and execution gates.
A CPU model, parsed source or container build does not prove GPU operation.
The source starter is built with `make starter` or
`python scripts/build_starter.py --output dist/ds60-classroom-starter.zip`; it
contains the maintained source and launcher, not Git history, learner data or
prebuilt images. See [validation](docs/validation.md) for its release checks.

## Database and dependency changes

Use only the local disposable `advanced_sql_training` database for automated
course SQL. `00_setup.sql` resets the course-owned `training` schema. Run with
`psql -X -v ON_ERROR_STOP=1`, respect declared persistent sequences, and never
redirect a test at a shared database. Bind SQL values and keep credentials out
of source, command arguments, outputs and progress notes.

Declare direct dependencies in the appropriate project group. Refresh
`uv.lock` with `uv lock` and verify `uv lock --check`; do not hand-edit it.
Worker-specific dependencies also have reviewed Docker locks and toolchain
contracts. An installable lock is not proof that every runtime or architecture
works. Document actual platform evidence separately from configuration.

## Optional CI skip for a prose-only push

GitHub supports the native token **`[skip ci]`**, with a space. The spelling
`[skip-ci]` is not supported by this feature. No custom workflow gate is needed.
After local documentation checks, an authorized commit can use:

```sh
git commit -m "docs: clarify setup [skip ci]"
```

Use this only when **every change in the push is documentation prose or its
regenerated readers**. Do not mix unvalidated code, executable lesson examples,
tests, runtime/configuration, dependencies or workflows into a push containing
a skip marker. GitHub evaluates commit messages in the push, so a marked docs
commit must not hide another implementation commit's checks.

Still regenerate readers and run the [local prose, rendering and link checks](docs/validation.md#optional-documentation-only-ci-skip).
The marker skips automatic push/pull-request runs; scheduled and manual runs
remain available, and jobs already running continue. Required PR checks can
remain Pending and block merging. Use an unmarked follow-up commit, or a manual
run only when repository policy accepts it. See [GitHub's skip documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).

## Submit a reviewable change

Explain the learner or contributor problem, the resulting behavior, the exact
checks run and any remaining limitations. Include reproduction steps for bugs
without private data. Keep the change focused, preserve stable IDs and progress,
and do not relax a verifier to conceal a failed example. Implementation changes
require CI for the submitted revision; the prose-only exception above still
requires local checks. Previous test counts do not establish current acceptance.

Before submission, review the diff for unintended generated data, outputs,
credentials, broken links and unrelated formatting. Follow repository review
policy for commits and publication. Local image builds do not authorize pushing
them to a registry.

Complete Python examples in the statistics book are the one fence-synchronization
exception: the full formatting command uses `scripts/sync_example_fences.py` to
copy each manifest-declared, styled example into its matching chapter fence only
after proving that the Python syntax trees and literal values agree. Other
fences and teaching strings retain their authored content. SQL formatting
preserves quoted values and entire dollar-quoted routine bodies exactly, and
checks PostgreSQL syntax trees plus psql controls before writing.
