# Repository guidance for agents

## Mission

Maintain a beginner-friendly, offline-after-bootstrap Python/data-science,
PostgreSQL, and application-engineering curriculum that runs on Windows,
macOS, and Linux. Accuracy and reproducibility matter more than preserving the
historical “60-day” shape.

## Start here

1. Run `git status --short --branch`; preserve unrelated work.
2. Read [README.md](README.md) and `curriculum/catalog.json`.
3. Read the closest nested `AGENTS.md` for files under `python/`, `sql/`, or
   `bridge/`.
4. Run commands from the repository root.
5. Use `python scripts/course.py doctor` before diagnosing environment failures.

## Sources of truth

- Lesson artifacts and `src/ds60sqlpy/catalog_builder.py`: inputs for lesson identity, ordering, prerequisites, dependency groups, network behavior, and artifact availability
- `curriculum/catalog.json`: checked-in generated index consumed by tools; regenerate it rather than editing it by hand
- `README.md`: learner entry point
- `docs/setup/`: operating-system setup
- `docs/content-authoring.md`: lesson contract
- `docs/validation.md`: verification policy
- `curriculum/practice_baseline.json` and `scripts/audit_practice.py`:
  immutable pre-enrichment counts and the per-surface exercise-doubling gate
- `scripts/build_course_guide.py`: source for generated `START_HERE.html`; never
  hand-edit the HTML
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

## Learner experience

- Assume no prior programming or database experience unless the learner says otherwise.
- Explain new terms before relying on them.
- Ask the learner to predict behavior and attempt exercises.
- Give progressive hints before opening or reproducing official solutions.
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
- PostgreSQL notebooks read only `DS60_DATABASE_URL`, pass an engine object to
  `%sql`, hide connection display, bind values, and tag live/non-Python magic
  cells for notebook-aware validation. Never put `%pip` or a password in a
  lesson notebook.
- Default lesson execution must work offline after setup.
- First-run Seaborn downloads are accepted but must be disclosed and cacheable.
- Pretrained model downloads and optional web resources must be explicit, tagged, and accompanied by a local fallback where practical.
- Never add an undocumented network dependency.

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

Do not expand the curriculum merely to increase lesson count. Add content only when it closes a documented learning gap.

## Validation

Use the narrowest relevant check during iteration, then run:

```text
python scripts/course.py doctor
python scripts/course.py catalog
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/build_course_guide.py --check
python scripts/scan_secrets.py --history
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

Portal changes must retain both delivery modes. `START_HERE.html` remains
self-contained and useful over `file://`; launcher mode binds only to
`127.0.0.1`, authenticates mutations with an in-memory session token, permits
no cross-origin writes, blocks hidden/sensitive paths, and maps explicit clicks
to a fixed VS Code/Jupyter action allowlist. Never add arbitrary shell text,
arbitrary path launch, remote binding, CORS, or a credential to the portal.

If a heavy or external prerequisite prevents a check, report the exact unverified surface.

## Safety

- Treat `sql/postgres-60day/00_setup.sql` as a destructive reset of the disposable `training` schema.
- Never point course reset commands at a production or shared database.
- Do not commit secrets, `.env` files, model caches, notebook checkpoints, or learner-local progress.
- Avoid destructive Git commands and broad cleanup.

## Serena and repository tools

Activate the Serena project and check onboarding when Serena is available. Use semantic tools for importable Python code, but remember:

- Notebooks are JSON documents; validate them with notebook-aware tools.
- SQL is not covered by the configured language servers; search with `rg` and prove behavior with PostgreSQL.
- Markdown/YAML indexing helps navigation but does not replace link or schema validation.

Keep durable truth in checked-in artifacts, authoring metadata, docs, and the regenerated catalog—not only in generated Serena memories.

## Scope boundaries

- `python/AGENTS.md` governs Python, notebooks, companion guides, and Python solutions.
- `sql/AGENTS.md` governs PostgreSQL scripts, guides, and SQL solutions.
- `bridge/AGENTS.md` governs Python/PostgreSQL integration lessons and tests.
- [CONTRIBUTING.md](CONTRIBUTING.md) contains the human contribution workflow.
