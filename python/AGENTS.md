# Python curriculum guidance

This file extends the root [AGENTS.md](../AGENTS.md) for `python/`.

## Runtime and commands

- Target Python 3.11–3.12; use Python 3.12 for canonical examples and CI.
- Run from the repository root.
- Use the repository `.venv`; prefer `python -m ...` over bare tool commands.
- On Windows, use `.\.venv\Scripts\python.exe`.
- On macOS/Linux, use `.venv/bin/python`.

## Learner notebooks

- Keep notebooks valid `nbformat` documents with the repository kernelspec.
- Prefer small, purposeful cells. Introduce one idea at a time.
- A lesson should contain objectives, explanation, runnable examples, exercises, self-checks, and next steps.
- Keep full worked answers in `solutions/`, not directly below learner exercises.
- Clear incidental execution outputs before committing unless an output is intentionally instructional.
- Do not commit widgets, local interpreter paths, timestamps, credentials, or machine metadata.
- Use deterministic seeds where randomness is not the lesson.
- Use notebook-aware tooling when editing; always run structural validation afterward.

## Python examples

- Use syntax supported by Python 3.11 unless a version-specific example is
  explicitly labeled and explained.
- Prefer standard-library solutions in early lessons.
- Use type hints and docstrings when they aid learning; do not bury beginners in unexplained abstractions.
- Use `pathlib.Path` and repository-relative paths.
- Write learner artifacts to ignored locations such as `artifacts/` or `.learning/`.
- Do not rely on cells having been run in a hidden order.
- Avoid shell magics for cross-platform tasks when Python can do the work portably.

## Dependencies and data

- Declare each directly imported third-party package.
- Keep core, advanced/heavy, and development dependencies separate.
- Do not assume a package is present because another dependency happens to install it.
- Prefer local, generated, or package-bundled datasets.
- Seaborn first-run dataset downloads are allowed when disclosed and cached.
- Tag pretrained model or other network downloads and offer an offline fallback.
- CPU execution is the default; GPU work must be optional.

## Validation

Run:

```text
python scripts/course.py validate
```

For a changed lesson, also verify:

- Notebook parses and opens.
- Relevant example cells execute from a fresh kernel.
- Imports match dependency metadata.
- Files are written only to documented locations.
- The lesson still works offline after any disclosed first-run cache.
- Companion guide, solution, catalog-builder inputs, and generated catalog entry agree.

When an artifact filename or solution availability changes, regenerate the index:

```text
python scripts/build_catalog.py
python scripts/course.py validate
```

Do not claim a notebook was executed when only its JSON was validated.
