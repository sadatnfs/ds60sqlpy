# SQL solutions

This folder contains worked solutions for the PostgreSQL exercises.

Current artifact coverage:

- Markdown explanations: Days 1–60
- Executable `.sql` solutions: Days 1–60

The classroom lists references per lesson. Prepared contributors can also use
`uv run --no-sync python scripts/course.py catalog --track sql` from the root.

## Conventions

- Solutions target the disposable `training` schema created by `00_setup.sql`.
- Markdown explains reasoning, tradeoffs, assumptions, and alternatives.
- Executable solutions include an explicit `search_path` and are intended for `psql`.
- Exercises that change data should remain rollback-safe unless persistence is explicitly stated.
- Days 38 and 39 include runnable single-session work plus explicit manual
  two-session instructions because isolation anomalies and deadlocks require
  genuine concurrency.
- Days 52–54 are the declared stateful solution sequence. Day 52 resets and
  commits the course-owned `dwh` schema; run Days 53 and 54 after it.

In the classroom, choose the solution artifact when ready to compare, then use
**Whole SQL lesson (psql)**. Read the transaction notes first, especially for
the stateful warehouse sequence. The transcript records the actual source and
result; reading a reference does not run it automatically.

Contributors preparing reference qualification should follow
[validation](../../../docs/validation.md) and use an explicitly selected local
disposable database. The full solution-sequence command supports a deliberate
reset, which replaces the course-owned schemas. It is not an ordinary learner
resume operation. Do not run it against valuable or shared data.

Try the learner exercise first. A solution is a comparison and explanation, not a replacement for the attempt.
