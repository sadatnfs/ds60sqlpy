# SQL Solutions — PostgreSQL Advanced SQL 60-Day Curriculum

This folder contains worked solutions for the practice exercises in each day’s lesson. Solutions are:
- Executable SQL with heavy inline commentary explaining the “how” and the “why”
- Written against the `training` schema created by 00_setup.sql
- Safe by default (no persistent DML unless explicitly noted); many examples use ROLLBACK wrappers

Conventions
- One file per day: `dayXX_solutions.sql`
- Each solution block is prefixed with the exercise statement for easy cross‑reference
- Where assumptions are needed (e.g., a status code), they are stated clearly and alternatives are suggested

Tip: Run with `psql -d advanced_sql_training -f sql/postgres-60day/solutions/dayXX_solutions.sql` to execute a whole file. Most files are segmented so you can copy/paste individual blocks.


Markdown deep-dive writeups
- In addition to executable .sql files, detailed, beginner-friendly explanations are available per day as .md files alongside each day’s .sql.
- Completed so far: Days 01–20 (day01_solutions.md … day20_solutions.md). More are being added continuously.
- Open the corresponding .md to read line-by-line commentary, pitfalls, and alternatives.
