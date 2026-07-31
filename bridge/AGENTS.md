# Agent guidance for the engineering bridge

This file governs everything under `bridge/`.

## Purpose and prerequisites

The bridge connects the Python and PostgreSQL tracks without becoming a second
beginner course. Day 1 follows Python Day 15 and SQL Day 15. Days 2–8 are
sequential. Preserve this dependency chain when changing lesson order.

## Artifact contract

Every day must have:

- one answer-free, syntax-valid learner file in `lessons/`;
- one companion guide in `companion-guides/`;
- one executable reference implementation and one reasoning-focused Markdown
  solution in `solutions/`;
- deterministic, fake-backed coverage in `tests/`.

Named modules under `bridge/professional/` follow the same separation but may
use a clean notebook as the learner/reference executable when the objective is
interactive SQL. PostgreSQL magic cells must be tagged
`skip-static-validation` and live cells must also be tagged `live-postgres`.

Companion guides include objectives, prerequisites, vocabulary, worked
examples, exercises, self-checks, common pitfalls, and a next step. Solution
notes discuss tradeoffs and failure behavior instead of merely repeating code.
Every guide must include a novice-safe `## How to run this lesson`, at least
two runnable topic-specific examples, an explicit Expected/Verify contract for
each exercise, and a final copy-ready `## Ask Codex about this lesson` prompt
using the exact stable ID and paths. The guide and solution must remain
self-contained when Codex is unavailable.
Each cataloged bridge module must meet its immutable
`curriculum/practice_baseline.json` target on learner, guide, and explanatory
solution surfaces with aligned, distinct numbered prompts.

## Database and security rules

- Target Python 3.11–3.12, PostgreSQL 16+, and Psycopg 3.
- Read the disposable course connection string from `DS60_DATABASE_URL`.
- Never commit or log credentials.
- Keep Psycopg imports inside optional live-DB boundaries when possible so core
  examples remain importable without the dependency.
- Bind values with `%s` and a separate parameter sequence.
- Use `psycopg.sql.Identifier` for dynamic table or column names. An allowlist
  is still required when the application controls the set of acceptable names.
- Do not use SQLite as a PostgreSQL test substitute.
- Make live steps opt-in, rollback-safe, and explicit about the target database.
- JupySQL notebooks use a SQLAlchemy engine with the explicit
  `postgresql+psycopg://` dialect, keep connection display disabled, and use
  named binding for values. Jinja SQL rendering is code generation and must
  not be presented as safe parameter binding.

## Teaching and typing style

- Use modern Python 3.11-compatible annotations: built-in generics, `X | None`,
  `Protocol`, `TypedDict`, `ParamSpec`, and abstract collection types.
- Prefer dependency injection and small Protocols so behavior can be tested
  without a database.
- Define a new term before relying on it.
- Do not call unfinished learner functions from `main()`.
- Do not leak solution code or answer-shaped pseudocode into learner files.
- Keep examples deterministic; inject clocks, sleepers, and external effects.
- Preserve input order when the lesson promises it.

## Validation

Run from the repository root:

```text
python -m compileall -q bridge
python -m pytest bridge/tests -q
python bridge/scripts/validate_bridge.py
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
ruff check bridge
ruff format --check bridge
```

Also check local Markdown links and `git diff --check`. Remove any generated
`__pycache__`, `.pytest_cache`, coverage, or learner-output files before
handoff.
