# Python curriculum guidance

This file extends the root [AGENTS.md](../AGENTS.md) for `python/`.

## Runtime and commands

Lead learner instructions with the Docker classroom. The host interpreter
commands below apply to the prepared contributor environment and optional
Jupyter workflows, not a second learner installer. Windows uses WSL 2.

- Target Python 3.11–3.12; use Python 3.12 for canonical examples and CI.
- Run from the repository root using the environment in [CONTRIBUTING](../CONTRIBUTING.md).
- Prefer `uv run --no-sync python ...` or the prepared `.venv/bin/python`.
- Browser Python runs use a fresh process for each Run; notebook kernels have
  their own state. Explain the selected route rather than implying equivalence.

## Learner notebooks

- Keep notebooks valid `nbformat` documents with the repository kernelspec.
- Prefer small, purposeful cells. Introduce one idea at a time.
- Historical Day 1–60 learner notebooks must contain at least eight purposeful
  cells, including at least three runnable code cells and enough explanatory
  Markdown to teach the lesson without an agent. These are minimums, not a
  reason to split prose or add filler.
- A lesson must contain objectives, a mental model and vocabulary, syntax
  anatomy, at least two runnable examples with predicted and observed
  behavior, guided and independent exercises, explicit expected/verify lines,
  common-error diagnosis, self-checks, and next steps.
- End every companion guide with the copy-ready, lesson-specific
  `## Ask an AI tutor about this lesson` contract defined in
  `docs/content-authoring.md`. The material before it must remain
  self-sufficient.
- Each cataloged lesson must meet its immutable
  `curriculum/practice_baseline.json` target on the learner notebook, guide,
  and explanatory solution. Count distinct numbered prompts, not hint or
  answer-step inflation.
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
- Named modules under `python/professional/` use stable catalog IDs rather than
  pretending to be extra numbered days. Keep their learner modules
  answer-free and their executable implementations under `solutions/`.

## Dependencies and data

- Declare each directly imported third-party package.
- Keep core, advanced/heavy, and development dependencies separate.
- Do not assume a package is present because another dependency happens to install it.
- Prefer local, generated, or package-bundled datasets.
- Default historical examples use the reviewed original offline fixtures through
  `ds60sqlpy.teaching_data`. Preserve their synthetic provenance and do not
  describe their results as historical or population evidence. A real external
  dataset/model is a separate explicitly prepared route, with its source,
  license, cache and availability assumptions stated.
- Tag pretrained model or other network downloads and offer an offline fallback.
- CPU execution is the default; GPU work must be optional.

## Source and fixture boundaries

The named language, NumPy, pandas and algorithm units are directly authored
four-artifact bundles. Their six tasks need complete code references and
explained answers; code-comment labels alone do not establish implementation
coverage. Use the actual shared depth and practice gates before admission.
The new legacy IDs live in `curriculum/extensions/python-modernization.json`
with their separate practice expansion targets. Preserve established IDs,
filenames, prerequisites and learner state.

Use `teaching_fixture` or `load_teaching_frame` for their fixed reviewed names.
A copied pad's `__file__` identifies a temporary submission, not the course root.
The thin Core worker has an explicit helper COPY and uses the fixed reviewed
course assets; do not relax its sanitized environment to discover them. Other
profiles need their own reviewed import/data preparation before using this API.

`python/authoring/` maintains only the synthetic fixture generator, not the
whole Python curriculum. Read its guide before regenerating data. Its exact
UTF-8 byte contract must agree with the loader's digest, including line endings.
Do not replace earlier execution receipts when a later prose or format change
is validated by a separately recorded parity mapping.

## Validation

Run:

```text
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
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
