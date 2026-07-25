# SQL solutions

This folder contains worked solutions for the PostgreSQL exercises.

Current artifact coverage:

- Markdown explanations: Days 1–60
- Executable `.sql` solutions: Days 1–60

Use `python scripts/course.py catalog --track sql` from the repository root for the generated availability view.

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

Run an available executable solution from the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day01_solutions.sql
```

Or validate the complete answer sequence, including the Days 52–54 warehouse
state contract:

```text
python scripts/course.py sql solutions --reset
```

`--reset` is destructive only to the disposable course schemas described in
the main SQL README.

Try the learner exercise first. A solution is a comparison and explanation, not a replacement for the attempt.
