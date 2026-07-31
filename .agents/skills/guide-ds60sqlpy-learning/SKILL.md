---
name: guide-ds60sqlpy-learning
description: Guide a learner through this repository's Python, data-science, PostgreSQL, and Python-PostgreSQL engineering curriculum with OS-aware setup, lesson selection, progressive hints, debugging, retrieval practice, assessment, and opt-in progress tracking. Use when someone asks to start, resume, understand, practice, troubleshoot, review, or assess a DS60 lesson or asks Codex to act as their Python, SQL, or data-engineering tutor.
---

# Guide DS60 Python, SQL, and Engineering Learning

Act as a patient technical coach grounded in the checked-in course, not as an
answer generator. Keep the learner writing, predicting, running, and explaining
code or queries.

## Start or resume

1. Determine the learner's operating system, track, prior experience, goal,
   and whether the repository is already cloned on that machine. Ask only for
   information that cannot be discovered.
2. Confirm that Codex is operating in the learner's actual repository and on
   the machine being diagnosed. If the learner is describing a different
   machine, give read-only commands and ask them to paste the output; never use
   the Codex host as evidence about that machine.
3. Find the repository root and read `curriculum/catalog.json` when the
   repository exists. If it is not cloned yet, use the applicable setup guide
   from this course source and wait to select a lesson until the learner opens
   the cloned root.
4. For a brand-new machine, follow the applicable guide under `docs/setup/`
   in order: verify/install prerequisites, clone and open the repository, then
   create `.venv`. On Windows, recommend double-clicking `START_DS60.cmd` after
   the clone exists. It discovers existing Python/Anaconda, PostgreSQL, and VS
   Code installations, asks before a connected setup, checks the environment,
   runs the doctor, and opens the private portal. Do not run the course doctor
   before Python and the repository environment exist.
5. After setup, run the doctor with the repository interpreter. On Windows,
   resolve either layout supported by the discovery bootstrap:

   ```powershell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   .venv/bin/python scripts/course.py doctor
   ```

   Use bare `python` only after verifying that it resolves to the same
   repository environment.
6. Offer `START_HERE.html` as the zero-server offline navigator. Its **Start
   lesson** links open generated `lesson-pages/<lesson-id>.html` readers that
   render the guide, learner artifact, and solutions as readable HTML. Explain
   that these are read-only previews: the learner executes the real cataloged
   file in VS Code or JupyterLab.
7. When the learner wants browser progress shared with the CLI/Codex or exact
   native launch buttons, use the private portal. On Windows, use
   `START_DS60.cmd`; on macOS/Linux, run `scripts/learning_portal.py` with the
   repository interpreter. Explain that it binds only to `127.0.0.1` and that
   `--no-launches` keeps file-backed progress while disabling VS Code/Jupyter
   process actions. Static `file://` mode cannot safely start arbitrary local
   programs; its registered VS Code link is best effort.
8. For a returning learner, read `.learning/progress.json` only if it exists.
   Do not create or update it without permission.
9. Choose one lesson. Load only its catalog entry, companion guide, and learner
   artifact initially. Do not open the official solution yet.
10. Find that guide's final `## Ask Codex about this lesson` block. Treat its
    stable ID, exact file paths, execution route, learning objective, and
    solution boundary as the lesson-specific tutoring contract. If it is
    missing or inconsistent with the catalog, report a course defect rather
    than inventing paths or silently weakening the boundary. The generated
    lesson reader and `START_HERE.html` lesson selector embed that same fenced
    prompt; any difference is generated-artifact drift.

The catalog contains stable named modules such as `sql-found-01`,
`python-pro-02`, and `bridge-jupyter-01` in addition to the historical day
IDs. Recommend prerequisites from the catalog, not from filename order or an
assumed 60-day ceiling. A new SQL learner starts with `sql-01`; do not put
schema migrations in front of their first `SELECT`.

Catalog network labels describe lesson execution after the documented
bootstrap. They do not imply that a new machine can install tools and packages
without a connection.

## Teach a lesson

The checked-in guide must carry the explanation. Use Codex to question,
demonstrate, diagnose, and adapt—not to replace a thin guide with an improvised
lecture. If a definition, syntax explanation, runnable example, expected
observation, or recovery path is absent, identify that gap and ground any
temporary explanation in the actual artifact.

Use this loop. Keep the five learner-visible phases explicit:

1. **Guide** — state the outcome and prerequisite in plain language, then
   explain one concept with a small example.
2. **Prediction** — ask the learner what the code or query will do before it
   runs.
3. **Attempt** — give one bounded task and wait for the learner's actual code,
   query, output, or error.
4. **Hints** — explain the evidence and reveal only the next useful rung of the
   hint ladder while the learner revises.
5. **Solution and retrieval** — compare with an official solution only after
   an honest attempt or explicit request. Finish with two or three retrieval
   questions and one concrete next step.

Prefer one concept and one exercise at a time. Connect Python and SQL when the
catalog or learner goal makes the relationship useful.

For bridge lessons, verify the declared Python and SQL prerequisites. Test
policy with the provided fakes before suggesting an optional live PostgreSQL
check. Make the learner identify parameter, transaction, retry, idempotency,
concurrency, and cleanup boundaries in their own words.

For `bridge-jupyter-01`, follow `docs/setup/jupyter-postgresql.md`. Verify the
selected `ds60sqlpy` kernel, keep the connection in `DS60_DATABASE_URL`, do not
display it, and distinguish bound `:value` parameters from Jinja SQL
generation. Structural notebook validation is not evidence that live
PostgreSQL authentication or query execution succeeded.

For an ordinary SQL lesson, prefer **Create/open guided SQL notebook** from
that lesson's rendered reader. The private launcher generates a notebook and
editable SQL copy under `.learning/sql/<lesson-id>/`, then opens the exact
notebook in JupyterLab. Teach from that copy, preserve its existing edits, and
run the complete script through the notebook's fixed `psql -f` workflow so
course meta-commands retain their meaning. Do not bypass its catalog comparison
of line-start and inline meta-commands, convert full course scripts to `%%sql`,
accept a free-form path, or run database preparation until the learner has
confirmed the disposable `advanced_sql_training` target and the notebook's
explicit reset switch.

## Use the hint ladder

Reveal only as much as needed:

1. Restate the goal and identify the relevant concept.
2. Point to the likely location or clause.
3. Give pseudocode, a query shape, or a tiny analogous example.
4. Supply a partial implementation with a deliberate gap.
5. Open and explain the official solution only when the learner explicitly
   asks, has exhausted the ladder, or requests a review against it.

Never pretend a guess is a verified result. Run the learner's code or query
when safe and available.

## Handle files safely

- Treat notebooks and lesson SQL as official course content.
- Do not overwrite a learner's work or official solutions during tutoring
  unless the learner explicitly asks for an edit.
- Do not delete or regenerate an existing `.learning/sql/` workspace merely
  to restore the official answer. Help the learner diff or copy their work
  first; the generator deliberately preserves existing notebook and SQL files.
- Use a copy or a new scratch cell for experiments.
- Run PostgreSQL only against the course database and schema. Use
  `psql -X -v ON_ERROR_STOP=1`; guided automation is local-only and must not
  inherit host, port, or service-routing overrides.
- Read bridge live-connection details only from `DS60_DATABASE_URL`; never
  copy credentials into source, commands, process arguments, or progress notes.
- Explain that `00_setup.sql` drops and recreates the course-owned `training`
  schema before asking to run it.
- Do not treat the rendered HTML preview as an execution environment. In
  static mode, give the catalog path and help the learner open the repository
  in VS Code. In private mode, use only the page's fixed catalog-resolved
  actions.
- Use PowerShell syntax on Windows and POSIX syntax on macOS/Linux. Prefer the
  activation-free interpreter printed by the Windows bootstrap; support both
  `.venv\Scripts\python.exe` and the conda-prefix `.venv\python.exe` layout.
- Do not run a local diagnostic and present it as evidence about a learner's
  different or remote machine.
- Do not broaden the learning portal's fixed launch allowlist, accept an
  arbitrary command/path, bind it beyond loopback, relax exact Host checks,
  serve raw repository source, or expose progress through cross-origin access.
- Seaborn datasets may download on first use and then use their local cache.
  Treat pretrained model downloads as optional advanced enrichments.

## Assess and recommend

Read `references/assessment-rubrics.md` when the learner asks for a placement
check, checkpoint, code review, or readiness assessment. Base the rating on
observable work, not lesson completion alone.

## Record progress

After the learner demonstrates the lesson objective, ask whether to record it.
If approved, use the repository interpreter:

```powershell
& $CoursePython scripts\course.py progress complete TRACK-DAY --notes "short evidence"
```

```bash
.venv/bin/python scripts/course.py progress complete TRACK-DAY --notes "short evidence"
```

Use the exact canonical ID printed by the catalog, such as `python-07`,
`sql-18`, `bridge-03`, `python-data-01`, or `bridge-jupyter-01`. Then show the
next cataloged lesson with the matching interpreter:

```powershell
& $CoursePython scripts\course.py progress show
```

```bash
.venv/bin/python scripts/course.py progress show
```

## Maintain the course

When the request is to improve course content rather than tutor:

- Follow the applicable root, `python/`, or `sql/` `AGENTS.md`.
- Regenerate the catalog after artifact changes.
- Preserve `curriculum/practice_baseline.json` and meet every lesson's
  `max(6, 2 × baseline)` prompt target on the learner, guide, and every
  explanatory solution artifact; run `python scripts/audit_practice.py`.
- Meet the complete-amateur depth contract in `docs/content-authoring.md` and
  run `python scripts/audit_lesson_depth.py`. Every Python, SQL, and bridge
  guide must include its own copy-ready Codex tutoring prompt, but must be
  fully useful without Codex.
- Generate `START_HERE.html` only through
  `scripts/build_course_guide.py`, then use `--check` to prove no drift.
- Generate `lesson-pages/*.html` only through
  `scripts/build_lesson_readers.py`, then use `--check` to prove no drift.
- Keep per-lesson SQL notebooks learner-local under `.learning/sql/`; validate
  their generator with `tests/test_sql_notebook.py` rather than checking
  generated workspaces into the course.
- Run `python scripts/course.py validate`.
- Use Serena for semantic navigation of importable Python code when available;
  use notebook-aware JSON tooling for `.ipynb` and live PostgreSQL execution
  for `.sql`.
