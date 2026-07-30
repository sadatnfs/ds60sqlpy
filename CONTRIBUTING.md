# Contributing

Contributions should make the course more accurate, runnable, teachable, and portable. Small fixes are welcome; broad curriculum changes should preserve the learner path and update its artifacts, authoring metadata, and generated index together.

## Before editing

1. Run all commands from the repository root.
2. Inspect the worktree:

   ```text
   git status --short --branch
   ```

3. Preserve unrelated changes. Do not reset, reformat, or regenerate files outside your task.
4. Read the applicable instructions:
   - [AGENTS.md](AGENTS.md)
   - [python/AGENTS.md](python/AGENTS.md) for Python or notebook work
   - [sql/AGENTS.md](sql/AGENTS.md) for SQL work
   - [bridge/AGENTS.md](bridge/AGENTS.md) for Python/PostgreSQL integration work
5. Check the generated lesson entry in `curriculum/catalog.json` and its inputs in the lesson artifacts and `src/ds60sqlpy/catalog_builder.py`.

## Set up and inspect the repository

Windows:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1
.\.venv\Scripts\python.exe scripts\course.py doctor
.\.venv\Scripts\python.exe scripts\course.py catalog
```

macOS or Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py catalog
```

See [Validation](docs/validation.md) for focused and full checks.

Optionally install the repository's local-only pre-commit hooks after setup:

```text
python -m pre_commit install
```

The hooks run the sensitive-content guard plus Ruff checks using the selected
environment; they do not fetch a third-party hook repository.

## Lesson content contract

Every learner-facing lesson should provide:

1. A clear title and level
2. Prerequisites
3. Learning objectives
4. A concise explanation of why the topic matters
5. Runnable examples using local or generated data by default
6. Exercises that progress from recall to application
7. Expected behavior or a way to self-check
8. A short knowledge check
9. Next steps
10. A separately located solution

Do not put the complete answer directly below an exercise in the learner artifact. Preserve the hint-first experience.
Every cataloged learner, guide, and explanatory-solution artifact must also
meet its immutable `curriculum/practice_baseline.json` target:
`max(6, 2 × audited baseline)`. Run `python scripts/audit_practice.py`; do not
lower the baseline or inflate counts with answer steps.

## Cross-platform requirements

- Support Windows PowerShell and POSIX shells explicitly.
- Do not label Bash syntax as PowerShell.
- Avoid `&&`, `||`, `source`, Bash line continuations, or `cat | command` in Windows snippets.
- Prefer `python -m pip` to a bare `pip`.
- Prefer activation-free Windows commands using `.\.venv\Scripts\python.exe`.
- Use `pathlib` in Python examples and repository-relative paths.
- Never use a developer-specific absolute path.
- Keep text files UTF-8 and follow [.editorconfig](.editorconfig) and [.gitattributes](.gitattributes).

## Offline-first requirements

The supported default is one connected bootstrap followed by offline coursework.

- Prefer generated data, tracked sample data, or packages that bundle their datasets.
- Tag and explain any first-run download.
- Do not add silent network calls.
- Record source, license, checksum, and refresh process for tracked datasets.
- Provide a local fallback when a remote model or dataset is only enrichment.

See [Offline use](docs/setup/offline.md).

## Dependency changes

- Add a dependency only when a lesson imports it directly or validation requires it.
- Put runtime, advanced/heavy, and development dependencies in the appropriate project group.
- Update the cross-platform `uv.lock` through the repository’s supported workflow.
- Verify the clean Python 3.12 path.
- Avoid relying on a transitive dependency for a direct import.

If `uv` is installed, refresh and verify the exact cross-platform resolution:

```text
uv lock
uv lock --check
```

Learner setup scripts use ordinary `pip` with the compatible ranges in
`pyproject.toml`; CI uses `uv.lock` so unexpected dependency drift is detected.
Do not hand-edit the lock.

## Notebook changes

- Use notebook-aware tooling; do not hand-edit large JSON blobs without validation.
- Keep valid notebook metadata and the repository kernel convention.
- Clear incidental outputs, timestamps, local paths, tokens, and generated artifacts.
- Seed random operations where teaching does not depend on randomness.
- Mark cells that intentionally require network, heavy dependencies, or manual interaction.
- Run structural validation and the appropriate execution check.

## SQL changes

- Target PostgreSQL 16+; canonical automation uses PostgreSQL 17.
- Execute with `psql -X -v ON_ERROR_STOP=1`.
- Use only the disposable training database and schema.
- Keep destructive setup explicit and idempotent where practical.
- Daily exercises should roll back unless persistence is a stated prerequisite.
- Multi-day projects must declare and validate persistent state rather than depending on a prior rolled-back lesson.

## Bridge changes

- Keep learner modules, guides, executable solutions, reasoning guides, and
  fake-backed tests aligned.
- Use Psycopg 3 parameter binding and explicit transaction ownership.
- Keep the default path offline; make live PostgreSQL checks opt-in,
  `DS60_DATABASE_URL`-driven, and safe for the disposable course database.
- Test pure policy separately from driver behavior and label what fakes cannot
  prove.

## Documentation changes

- Use relative Markdown links for repository files.
- Run internal-link and catalog validation.
- Keep commands rooted at the repository root.
- Avoid duplicating long setup procedures; link to the canonical OS guide.
- Replace stale progress prose with catalog-derived status where possible.
- Edit `scripts/build_course_guide.py`, not generated `START_HERE.html`, and
  run its `--check` mode.
- Preserve both portal modes and the loopback/token/origin/path/launch
  allowlist boundary documented in `docs/learning-portal.md`.

## Catalog changes

`curriculum/catalog.json` is generated and checked in so learners and tools can inspect it without running a build first. Do not edit it by hand.

When a lesson filename, solution availability, phase rule, dependency group, prerequisite rule, or network classification changes:

```text
python scripts/build_catalog.py
python scripts/course.py validate
git diff --exit-code -- curriculum/catalog.json
```

The final command is a CI drift check; run it only after the regenerated file is staged as the intended output or use `git diff -- curriculum/catalog.json` to review a local change.

## Before submitting

Run:

```text
python scripts/course.py doctor
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/build_course_guide.py --check
python scripts/scan_secrets.py --history
```

Then check:

- The relevant lesson works from a clean environment.
- The default lesson path works offline after bootstrap.
- Windows and POSIX instructions are both valid.
- The catalog matches files and prerequisites.
- No learner answer was accidentally placed in the exercise artifact.
- No generated data, model, notebook checkpoint, secret, or local configuration was added.
- `git diff --check` passes.

In your change summary, state what you validated and what you could not validate.
