# Scala and Apache Spark study guide

This page holds the operating steps that every lesson in the course shares: how to run a pad,
which files belong to a lesson, how to practice, and how to read the evidence a run produces.
Each lesson guide links here instead of repeating these steps, so the lesson pages can spend
their words on the lesson's own data and contracts.

## Run a language lesson

Lessons spark-002 through spark-010 are Scala language lessons. Open the lesson in the
classroom, select the Scala source and prepare the `scala-jvm` profile. Save your pad, then
run it. The classroom stages the pad as `Main.scala`, so keep the `object Main` entry point and
its `main` method. The prepared worker compiles and runs one bounded program on JDK 17 with
Scala 2.13. No source file installs a tool or downloads a dependency.

If the profile is unavailable on your machine, reading, editing and saving still work. Write
down the values you predict for each exercise and run the pad later; do not treat a saved pad
as a passing one.

## Run a paired lesson

Lessons from spark-011 onward (except the reading lessons spark-030 and spark-040) ship the
same contracts in Scala and in PySpark. Choose the language you understand, prepare only its
profile (`spark-local-scala` or `spark-local-python`), save the pad and run the complete
source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with an
`if __name__ == "__main__":` guard.

Every paired program owns its engine for the length of one run:

- it creates its own `local[2]` session rather than attaching to a shared notebook session;
- it disables the Spark UI, binds the driver to the loopback address and sets the session
  time zone to UTC;
- it builds its fixture inside `main`, so there is no hidden notebook state to reproduce;
- it stops the session in a `finally` block, even when an assertion fails.

No paired lesson reads an external dataset, downloads a package, opens a JDBC connection or
calls a cloud service. Reading lessons need no runtime at all.

## Scratch directories and streaming

File and streaming lessons create a fresh scratch root inside their own job directory, write
only below it and remove only what they created. Finite streaming lessons use bounded inputs
and the `availableNow` trigger, wait for the query to finish and stop the query
they started. A lesson never resets an existing checkpoint, deletes unrelated learner work or
connects to a running service. If a run is interrupted, delete the lesson's own scratch root
before trying again rather than pointing the lesson at an older checkpoint.

## Lesson files

Each lesson has the same set of files:

- a **guide** in `guides/` with vocabulary, two worked examples, six exercises and checks;
- a **learner pad** in `lessons/` (one `.scala` file for language lessons, a `.scala` and a
  `.py` file for paired lessons). Running it before you write anything executes the two
  worked examples and reports that six task implementations remain;
- a **reference program** in `solutions/` for each language, with every task implemented and
  asserted against literal expected values;
- **explained solutions** (`solutions/<id>_solutions.md`) that walk through each exercise.

Open the explained solutions only after an honest attempt or when you deliberately want a
worked comparison. A bounded `collect` appears only on the declared tiny fixtures; do not copy
that pattern onto a large or unbounded table.

## Practice routine

Use the same loop for every exercise:

1. Read the contract and the fixture, then predict the exact result, including counts, NULLs
   and ordering.
2. Attempt the implementation in your pad and run it.
3. If you are stuck, read one progressive hint, not all of them, and try again.
4. Compare your output with the exercise's expected result and verification line. Keep the
   observed values, not only a success message.
5. Close the pad and explain the mechanism in your own words. Then change one fixture value
   and predict the new result before running again.

Move to the next lesson once you can explain the boundary behavior of each exercise, not just
reproduce the happy path. The [course route](README.md) lists the lesson order.

## Three kinds of evidence

A run can show three different things, and they are easy to confuse:

- **Process success.** The program compiled, ran and exited cleanly. Compilation alone proves
  nothing about values, missingness, identity or failure behavior.
- **Logical correctness.** The assertions compare results with literal expectations written
  from the fixture. In paired lessons the Scala and PySpark versions each check against those
  literals, because two implementations that agree with each other can still share the same
  mistake.
- **Understanding.** You can predict a changed fixture, explain a counterexample and say why a
  tempting wrong implementation fails a specific assertion. Only you can supply this one.

A local run is also not evidence about a cluster. Plans, partition counts and timings from a
`local[2]` session say nothing reliable about cluster-scale performance, production recovery or
an exactly-once guarantee. The references are executable explanations, not a hidden grading
service.

## Versions

The [execution baseline](execution-baseline.md) pins the prepared family: Spark 4.3.0, Scala
binary 2.13, JDK 17 and Python 3.12. Several references print the versions they actually ran
with; compare those readbacks with the baseline instead of assuming the builder settings were
accepted.
