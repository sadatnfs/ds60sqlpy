# Repository guidance for agents

## Mission

Maintain a beginner-friendly, offline-after-setup curriculum spanning data
science, statistics, machine learning, languages and systems. The primary
application is one Docker browser classroom at `/classroom` on Windows, macOS
and Linux. Python, PostgreSQL, bridge, languages, systems and the tutorial books
share its subject chooser and workspace. Accuracy and reproducibility matter more than preserving the
historical “60-day” shape.

## Start here

1. Run `git status --short --branch`; preserve unrelated work.
2. Read [README.md](README.md) and `curriculum/catalog.json`.
3. Read the closest nested `AGENTS.md` for files under `python/`, `sql/`, or
   `bridge/`.
4. Run commands from the repository root.
5. Diagnose the selected route: Docker engine/Compose and the app profile
   readiness for the classroom; `python scripts/course.py doctor` only for an
   explicitly prepared native Python environment. Host Python is not a classroom
   prerequisite.
6. Use parallel agents for independent work with clear file ownership. Keep
   image builds sequential and use grouped four-worker tests. Preserve human
   Git actions and unrelated workloads. Do not use em dashes in authored prose.

## Sources of truth

- Lesson artifacts and `src/ds60sqlpy/catalog_builder.py`: inputs for lesson identity, ordering, prerequisites, dependency groups, network behavior, and artifact availability
- `src/ds60sqlpy/catalog.py`: catalog loading and learner-facing ordering;
  named modules can use an explicit order override to appear at their
  prerequisite milestone without renumbering the historical day tracks
- `curriculum/catalog.json`: checked-in generated index consumed by tools; regenerate it rather than editing it by hand
- `curriculum/extensions/*.json` and
  `src/ds60sqlpy/curriculum_framework.py`: additive track, lesson, and goal
  registration plus explicit runner capabilities. Use
  [the extension playbook](docs/curriculum-extension-playbook.md) before adding
  a language, operations topic, or reading-only track.
- `README.md`: learner entry point
- `docs/setup/`: operating-system setup
- `docs/content-authoring.md`: lesson contract
- `docs/curriculum-design-references.md`: source-backed teaching patterns and
  the rationale for the repository's lesson sequence
- `docs/validation.md`: verification policy
- `curriculum/practice_baseline.json` and `scripts/audit_practice.py`:
  immutable pre-enrichment counts and the per-surface exercise-doubling gate
- `scripts/audit_lesson_depth.py` and `docs/lesson-depth-report.md`:
  structural minimums for self-contained beginner explanations, runnable
  examples, exercise contracts, explanatory solutions, Python
  notebook depth, and per-lesson Codex prompts across all three tracks
- `scripts/build_course_guide.py`: source for generated `START_HERE.html`; never
  hand-edit the HTML
- `src/ds60sqlpy/lesson_reader.py` and `scripts/build_lesson_readers.py`:
  sources for generated `lesson-pages/<lesson-id>.html` and linked
  `reference-pages/<source>.html`; never hand-edit those readers
- `src/ds60sqlpy/sql_notebook.py` and
  `scripts/build_sql_lesson_notebook.py`: catalog-restricted generator and
  runner for learner-local SQL notebooks under `.learning/sql/`; never check
  generated workspaces into Git
- `classroom` and `scripts/classroom.sh`: shared build/start/health/browser entrypoint
  for macOS, Linux and Windows through WSL 2. It defaults to all ordinary profiles
  and automatic loopback host ports. Preserve explicit overrides and named data.
- `START_DOCKER_CLASSROOM.cmd`, `START_DOCKER_CLASSROOM.command` and
  `compose.classroom.yaml`: primary Docker-only classroom and named-volume
  persistence. See `docs/docker-classroom.md`; compiler/framework profiles run
  inside images, and the thin launchers discover the actual published port.
- `START_DOCKER_LAB.cmd` and `scripts/start_docker_windows.ps1`: optional older
  Windows installation wizard, including consented prerequisite setup.
  Re-detect after a manual reboot; preserve existing engines and learner work.
- `START_DS60.cmd` and `scripts/start_ds60.ps1`: optional Windows native entry point;
  keep it path-safe, PowerShell 5.1-compatible, and aligned with
  `scripts/bootstrap_windows.ps1`
- `src/ds60sqlpy/portal.py`: optional loopback launcher and shared
  `.learning/progress.json` boundary
- `docs/curriculum-gap-backlog.md`: implemented gap record and maintenance
  rules
- `.agents/skills/guide-ds60sqlpy-learning/`: Codex tutoring workflow
- `bridge/README.md` and `bridge/AGENTS.md`: the integration track's learning
  and engineering contracts
- `python/professional/`, `sql/professional/`, and `bridge/professional/`:
  named modules that extend the stable Days 1–60 without renumbering them

Do not hand-maintain a second lesson inventory when it can be derived from the generated catalog.

## Supported baseline

- Python 3.11-3.12; 3.12 is the canonical and recommended version
- PostgreSQL 16+; canonical automation uses PostgreSQL 17
- VS Code as the documented editor
- JupySQL with SQLAlchemy's explicit Psycopg 3 dialect for the optional
  PostgreSQL-in-Jupyter lesson
- One connected bootstrap, then offline study

Use `python -m pip`, repository-relative paths, and `pathlib`. Never add a developer-specific absolute path.

## Explicit tutorial-book exception

The statistics/ML book is a tutorial, as explicitly requested by the user.
Its `learning_mode: tutorial` content must include detailed theory, worked
examples and answered interview discussions, with no exams, problem sets,
prediction gate or withheld solutions. Its manual read marker is not mastery.
Use the book's coverage and executable-example tests instead of applying the
practice exercise-count rules below. Ordinary programming and systems lessons
retain their full practice contracts. New subjects use the module extension
contract in `docs/implementation/ADDING_A_MODULE.md`; do not hardcode five subjects.

## Learner experience

- Assume no prior programming or database experience unless the learner says otherwise.
- Explain new terms before relying on them.
- Make the checked-in lesson sufficient on its own. Codex coaching is an
  optional practice aid, never a substitute for definitions, syntax anatomy,
  examples, expected observations, or troubleshooting in the lesson.
- Ask the learner to predict behavior and attempt exercises.
- Give progressive hints before opening or reproducing official solutions.
- Use the sequence **guide → prediction → learner attempt → progressive hints
  → solution comparison**. Opening a file or checking a box is not evidence of
  mastery.
- Treat every rendered lesson page as a readable, read-only preview. In the
  coding lab, use the lesson's capability notice and saved pad/evidence route.
  Native editor/Jupyter and generated `.learning/sql/` working copies remain
  alternatives. A reading lesson needs written reasoning, not an invented run
  command or an automatic completion.
- Do not overwrite learner work.
- Keep solutions separate from learner artifacts.
- Do not silently skip failures or hide exceptions that teach an important concept.

## Cross-platform and offline rules

- Shared prose must include valid Windows PowerShell and POSIX variants when commands differ.
- Do not use Bash syntax in a PowerShell block.
- On Windows, use the interpreter printed by `bootstrap_windows.ps1` so
  activation policy is not a blocker. A standard environment uses
  `.\.venv\Scripts\python.exe`; the conda-prefix fallback uses
  `.\.venv\python.exe`. When the layout is not known, test those two paths in
  that order rather than assuming one.
- Windows startup must keep `-DiagnosticsOnly -NonInteractive` read-only and
  require explicit acknowledgement before a noninteractive connected setup.
  It may rediscover tools and change only its process-local `PATH`; never add
  credentials or an automatic database reset.
- PostgreSQL notebooks read only `DS60_DATABASE_URL`, pass an engine object to
  `%sql`, hide connection display, bind values, and tag live/non-Python magic
  cells for notebook-aware validation. Never put `%pip` or a password in a
  lesson notebook.
- Default lesson execution must work offline after setup.
- First-run Seaborn downloads are accepted but must be disclosed and cacheable.
- Pretrained model downloads and optional web resources must be explicit, tagged, and accompanied by a local fallback where practical.
- Never add an undocumented network dependency.
- A static `file://` page may render course content and offer a best-effort
  registered VS Code URL, but it cannot safely start local programs. Keep
  native actions in the authenticated private launcher and never regress to
  opening raw Markdown, notebooks, Python, or SQL as the browser lesson view.
- User-facing local Markdown and SQL links from the dashboard, lesson readers,
  and rendered references must resolve to generated HTML rather than raw
  browser source. In static mode, record completion on `START_HERE.html`; only
  authenticated loopback readers expose their own completion checkbox.
- Guided SQL notebooks must be derived from a stable catalog ID, write only
  beneath ignored `.learning/sql/`, preserve an existing learner notebook and
  SQL copy, run complete course scripts through fixed non-shell `psql -f`
  commands, reject line-start or inline changes to cataloged `psql`
  meta-commands, and require an explicit reset confirmation before preparing
  the disposable course schema.
- Every automated course SQL path, including doctor and `SqlRunner`, must
  validate the exact local disposable `advanced_sql_training` target, reject
  remote/multi-host and routing/service URL or environment overrides, and pass
  a password-bearing target through the child environment rather than the
  process argument list.

## Content changes

For each lesson change:

1. Confirm prerequisites and level.
2. Keep guide, learner artifact, solution, catalog inputs, generated index, and navigation aligned.
   Named professional guides must spell out every direct catalog prerequisite
   with its exact backticked stable ID.
3. Use deterministic examples unless randomness is the topic.
4. Declare every direct dependency.
5. Include a self-check or expected behavior.
6. Update documentation when commands or behavior change.
7. Meet the audited practice target on the learner, guide, and every
   explanatory-solution artifact: at least `max(6, 2 × baseline)`, using
   distinct prompts rather than relabeled answer steps.
8. Regenerate both navigation layers after artifact or catalog changes:
   `START_HERE.html` and every affected `lesson-pages/<lesson-id>.html`.
9. Meet `docs/content-authoring.md` and `scripts/audit_lesson_depth.py`: define
   the mental model, explain syntax or query anatomy, include at least two
   topic-specific runnable examples, label the expected result or verification
   for every numbered exercise, explain common mistakes, and end every guide
   with `## Ask Codex about this lesson`.
10. Make that Codex prompt copy-ready and lesson-specific. It must name the
    stable lesson ID, exact guide and learner paths, the
    `guide-ds60sqlpy-learning` skill, the `solutions/` boundary, and the
    explain → predict → attempt → one hint → evidence → retrieval loop.
    The guide's fenced prompt is the source used by both the lesson reader and
    `START_HERE.html`; do not maintain separate prompt prose in generated HTML.
11. Make each `Expected`/`Verify` contract independently inspectable. It may
    not merely restate the exercise or apply a generic checklist unrelated to
    that exercise's mechanism.

Do not expand the curriculum merely to increase lesson count. Add content only when it closes a documented learning gap.

For future tracks, keep these extension boundaries:

1. Author content under `courses/<track>/` with a plan and a local `AGENTS.md`.
   Register it through an additive manifest; keep historical IDs, day values,
   and the immutable practice baseline intact.
2. Separate a subject from its execution tool. Deep learning can use the
   Python runner; LLM theory can use `none`. C++, Scala/Spark, and Kubernetes
   descriptors do not by themselves implement execution.
3. Add every new lesson to `curriculum/practice_expansion.json` with baseline
   zero and target six. The guide, learner, and every explanatory solution
   still need six distinct, inspectable exercises and the full depth contract.
4. A `none` lesson requires a separate explanatory solution and worked
   reasoning with expected observations. Other runners require two solution
   artifacts, including an explanation. Do not generate filler to pass counts.
5. Do not place shell text, image commands, cluster targets, or credentials in
   a manifest. Actual adapters belong in reviewed backend code and require
   bounded execution, truthful capability reporting, and failure/cleanup tests.
6. Regenerate the catalog, dashboard, lesson readers, and reference pages.
   Prove search, prerequisite plans, the app, and MCP discover the new IDs in
   an isolated fixture before claiming a track is integrated.

## Validation

Use the narrowest relevant check during iteration, then run:

```text
python scripts/course.py doctor
python scripts/course.py catalog
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
python scripts/scan_secrets.py --history
python -m pytest tests/test_course_guide.py tests/test_lesson_depth_audit.py tests/test_lesson_reader.py tests/test_portal.py tests/test_sql_notebook.py tests/test_windows_startup.py
```

SQL commands must use:

```text
psql -X -v ON_ERROR_STOP=1 ...
```

Definition of done:

- A regenerated catalog has no drift and its paths agree.
- Notebook and JSON structure is valid.
- SQL-magic notebooks receive structural validation offline and an explicitly
  reported live execution check against only the disposable course database.
- Relevant runnable examples execute.
- SQL is tested against a clean disposable database.
- Bridge modules pass fake-backed tests; optional live checks use only the
  disposable course database.
- Internal links resolve.
- Offline behavior is preserved.
- Windows and POSIX instructions remain valid.
- Generated artifacts, caches, credentials, and unrelated diffs are absent.
- `docs/practice-coverage.md` and `docs/lesson-depth-report.md` match their
  generators, and all cataloged Python and SQL lessons pass both gates.

Portal changes must retain both delivery modes. `START_HERE.html` remains
self-contained and useful over `file://`; launcher mode binds only to
`127.0.0.1`, authenticates mutations with an in-memory session token, permits
no cross-origin writes, requires the exact Host on every request, serves only
generated guide/lesson/reference HTML, and maps explicit clicks to a fixed
VS Code/Jupyter action allowlist. Never add arbitrary shell text, arbitrary
path launch, remote binding, CORS, or a credential to the portal.
`--no-launches` must continue to provide file-backed progress without native
process actions.

If a heavy or external prerequisite prevents a check, report the exact unverified surface.

## Safety

- Treat `sql/postgres-60day/00_setup.sql` as a destructive reset of the disposable `training` schema.
- Never point course reset commands at a production or shared database.
- Do not commit secrets, `.env` files, model caches, notebook checkpoints, or learner-local progress.
- Treat ignored learner state as private, not disposable. Do not remove
  `.learning/progress.json`, `.learning/sql/`, `artifacts/`, or `mlruns/`
  without confirming what the learner wants to preserve.
- Avoid destructive Git commands and broad cleanup.

## Serena and repository tools

Activate the Serena project and check onboarding when Serena is available. Use semantic tools for importable Python code, but remember:

- Notebooks are JSON documents; validate them with notebook-aware tools.
- SQL is not covered by the configured language servers; search with `rg` and prove behavior with PostgreSQL.
- Markdown/YAML indexing helps navigation but does not replace link or schema validation.

Keep durable truth in checked-in artifacts, authoring metadata, docs, and the regenerated catalog - not only in generated Serena memories.

## Scope boundaries

- `python/AGENTS.md` governs Python, notebooks, companion guides, and Python solutions.
- `sql/AGENTS.md` governs PostgreSQL scripts, guides, and SQL solutions.
- `bridge/AGENTS.md` governs Python/PostgreSQL integration lessons and tests.
- [CONTRIBUTING.md](CONTRIBUTING.md) contains the human contribution workflow.

## Expansion implementation checkpoint

Read [the implementation checkpoint](docs/implementation/CHECKPOINT.md) before
continuing the expanded module and tutorial-book library. Read [the module authoring contract](docs/implementation/ADDING_A_MODULE.md)
when extending a subject or adding a language. Authored lesson files live in
`courses/` and are
loaded by `modules.py`; they do not silently replace the published catalog.
`module_jobs.py` owns persisted jobs, `module_service.py` authenticated app
actions, and the optional `module_worker.py` / `worker_operations.py` pair owns
bounded private-worker execution. Every claimed runtime needs an actual Docker
receipt. Preserve private runtime session files outside `.learning`, and never
print their credentials. Keep image builds sequential under the measured disk
budget. Do not start unrelated containers or change the engine configuration.

## Guided application and Codex adapter

- Read [the expansion design hub](docs/expansion/README.md) before adding Kubernetes, TensorFlow, LLM, C++, or Scala/Spark content. Subject plans, pilot lessons, typed job boundaries, profile qualification, and publication gates live there.
- Planning JSON under `docs/expansion/plans/` is design-only. Validate it with `scripts/build_journey_preview.py --check`. Never copy it into active extensions or advertise runtime support until the lesson and profile pass the documented gates.
- The journey preview generator and templates are developer-only design archives.
  `/journey-preview`, `/learn` and `/journeys` are compatibility aliases for the
  same `/classroom` shell. Do not restore separate learner interfaces.

- `scripts/learning_lab.py` and `src/ds60sqlpy/lab.py` are the explicit trusted-code coding application. The original portal retains its fixed action allowlist.
- The coding lab executes learner-submitted Python and SQL through bounded backend processes. Preserve exact Host, origin, token, request-size, output-size, and target-database checks. Do not describe this personal environment as a security sandbox for untrusted code.
- Only explicit container mode binds the coding app inside its container namespace; Compose publishes only loopback host ports. Native mode stays loopback-only.
- `src/ds60sqlpy/coaching.py` and `study_plan.py` provide shared lesson/evidence and prerequisite planning for the app and MCP adapter.
- The MCP server uses the official optional SDK over stdio, exposes no code execution, and is read-only unless its progress-write flag is explicitly enabled. Official solutions require a separate explicit reveal.
- `scripts/build_app.py` bundles only an allowlisted course payload. Never package learner pads, progress, credentials, Git history, caches, or a developer environment. Existing workspaces are preserved.
- New lessons use the separate `curriculum/practice_expansion.json`; the July historical baseline stays unchanged. Both structural and depth audits apply.
- Run the app, backend, and MCP tests after changes. A native build validates only its actual OS and architecture. Docker configuration or CI definitions do not prove that an image was built or started.

## Unified presentation and saved work

- `src/ds60sqlpy/classroom.py` derives the combined subject directory from both
  canonical catalogs. Add metadata through the existing catalog or module
  contract; never maintain a second hand-written lesson list in the UI.
- `assets/classroom.html`, `classroom.css` and `classroom.js` own the single
  learner interface. Subject themes, keyboard navigation, save barriers and
  language/mode-specific drafts must remain coherent. The two superseded UI
  templates are removed. Run `node scripts/check_classroom_ui.mjs` after changes.
- `lesson_reader.py`, `reader_math.py` and `reader_content.py` provide shared
  offline math and syntax rendering for the app and static readers. Use explicit
  LaTeX delimiters and tagged code fences. Never reinterpret code as equations,
  enable raw active HTML, load a CDN, or edit executable examples to fix typography.
- Run `python scripts/normalize_lesson_prose.py --write` after subject authoring
  generators and before HTML generation. Its reviewed registries are durable
  inputs; ambiguous words require editorial review, never automatic splitting.
  `python scripts/check_content_rendering.py` rejects unsupported published math.
- `ClassroomRunStore` retains immutable Python/SQL run receipts beneath the
  learning-state directory. It complements saved source versions and the module
  job store. A completed execution and a failed receipt write are distinct
  outcomes. Never replay code automatically to repair storage or reconnect.
- Preserve existing lesson IDs, old saved pads, coaching phases, module drafts,
  job receipts and all named Docker learning volumes. Code/result history is
  scoped by lesson, language and SQL mode. Viewing past results must not replace
  the current editor or claim automatic mastery.
- `make classroom`, `classroom-build`, `classroom-start` and `classroom-stop`
  delegate to the shared `./classroom` entrypoint. Keep build, readiness and
  published-port logic in that single implementation.
