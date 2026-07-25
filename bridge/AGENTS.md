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

Companion guides include objectives, prerequisites, vocabulary, worked
examples, exercises, self-checks, common pitfalls, and a next step. Solution
notes discuss tradeoffs and failure behavior instead of merely repeating code.

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
ruff check bridge
ruff format --check bridge
```

Also check local Markdown links and `git diff --check`. Remove any generated
`__pycache__`, `.pytest_cache`, coverage, or learner-output files before
handoff.
