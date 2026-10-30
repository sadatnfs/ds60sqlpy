# SQL-START-03: Query Construction and Debugging

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-start-03**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-start-03/lesson/workspace/sql/professional/lessons/sql_start_03_query_debugging.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-start-03
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** foundation
- **Direct catalog prerequisites:** [`sql-start-02`](sql_start_02_values_null_order.md)
- **Artifacts:** [learner SQL](../lessons/sql_start_03_query_debugging.sql), [solution reasoning](../solutions/sql_start_03_query_debugging_solutions.md), [executable solution](../solutions/sql_start_03_query_debugging_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Build a query one clause at a time and inspect surviving identities.
- Separate parser/name errors from a syntactically valid wrong answer.
- Explain Boolean grouping, alias scope, and first-error recovery using a small fixture.

## Vocabulary and concepts

Debugging means locating the first place where observed behavior differs from
the intended question. It is not guessing different punctuation until a query
returns something. Start with the output sentence, choose the input, inspect
its identities, add one restriction, and check again. This lesson has six
tasks, so you can predict every intermediate result by hand. The small scale
lets you reason before relying on a database error or an assistant.



- **Syntax error:** A syntax error means PostgreSQL cannot parse the statement into valid
SQL grammar. 

- **Name error:** A name error means the statement refers to a column or other
object PostgreSQL cannot resolve. 

- **Semantic error:** A semantic error means the query runs
but answers the wrong question. 

- **Sqlstate:** A SQLSTATE is a five-character code
identifying an error category independently of localized message wording.


- **Alias scope:** Alias scope describes where a name created with AS is available.


- **Checkpoint:** A checkpoint is a deliberately small intermediate query whose returned
identities can be compared with the question before more logic is added.

The debugging loop is question, prediction, execution, comparison, smallest
repair. A zero-row answer is not necessarily an error. A successful command
exit is not proof of a correct business answer. Record the actual SQL and
complete first error when asking for help. If psql is waiting at a continuation
prompt, inspect whether the semicolon or quote is unfinished before opening a
second terminal. `\r` clears an unfinished interactive query buffer; it is
not a database rollback and is not needed in the course file.

## Syntax anatomy and query reasoning

For `SELECT task_id, effort * 2 AS doubled_effort FROM start_tasks WHERE
effort * 2 >= 6 ORDER BY task_id;`, FROM introduces the task columns and
WHERE filters input rows before SELECT exposes the output alias. Therefore
`WHERE doubled_effort >= 6` cannot use that alias at the same query level.
Repeat the expression for now. Later, a subquery or common table expression
can make a calculated value an input to another query. ORDER BY can refer to
a SELECT alias because it orders the final output.

Parentheses state Boolean grouping. AND binds more tightly than OR, so
`team = 'Red' AND status = 'open' OR status = 'blocked'` admits every blocked
task regardless of team. If the question requires Red tasks in either state,
write the grouping around the status alternatives. Parentheses do not merely
decorate a predicate: they change which rows qualify. Trace one Blue blocked
task to expose the difference without a large dataset.

Each query follows FROM, WHERE, SELECT, ORDER BY, LIMIT for this lesson's
logical reasoning. The physical execution plan is PostgreSQL's concern and
may differ. Keep a unique task_id in diagnostic output and compare complete
ID lists. Repairing an unknown-column spelling does not prove the threshold
or grouping is right, so rerun the evidence checks after the syntax repair.
The fixture includes an effort exactly 3, a missing effort, and a blocked Blue
task to exercise three different boundaries rather than relying only on a
comfortable normal case.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: Watch a predicate narrow the identities

```sql
SELECT
  task_id,
  team,
  status,
  effort
FROM
  start_tasks
WHERE
  status = 'open'
ORDER BY
  task_id;
```

Start with all six task identities. The status condition keeps 1,3,4,5, including the task with unknown effort because this predicate does not inspect effort. If your prediction omitted ID 3, you added an unstated assumption. Check this stage before introducing an effort threshold. The output is one open task per task_id, not one team.

**Expected:** Four rows, columns task_id, team, status, effort; IDs 1,3,4,5. ID 3 still has NULL effort.

### Example 2: Compute a label without using it too early

```sql
SELECT
  task_id,
  effort * 2 AS doubled_effort
FROM
  start_tasks
WHERE
  effort * 2 >= 6
ORDER BY
  doubled_effort DESC,
  task_id;
```

The filter repeats the arithmetic because doubled_effort is an output name unavailable to WHERE at this query level. ORDER BY can use the alias. The unknown effort yields an unknown comparison and does not qualify. The expression does not alter stored effort. Sorting ties by task_id makes the two doubled values of 6 appear in a declared order.

**Expected:** Three rows with columns task_id, doubled_effort: (2,10), (4,6), (5,6).

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Build a checkpoint.**

   **Inputs/evidence:** For sql-start-03 Exercise 1, Return Red open tasks with task_id, team, status, effort. First predict all Red IDs and then the IDs remaining after the open restriction.

   **Expected result/shape:** For sql-start-03 Exercise 1, Two task rows with columns task_id, team, status, effort; final ORDER BY task_id: IDs 1 and 5. The Red-only checkpoint has IDs 1,2,5.

   **Verify:** For sql-start-03 Exercise 1, Inspect the Red-only stage IDs 1,2,5, then confirm only 1,5 remain after the status filter. Task 2 is the closed negative control.

   **Progressive hint:** Add one AND restriction after confirming the first filter.

2. **Repair alias scope.**

   **Inputs/evidence:** For sql-start-03 Exercise 2, Repair SELECT task_id, effort * 2 AS doubled_effort FROM start_tasks WHERE doubled_effort >= 6. Return task_id, doubled_effort in ascending task_id order without introducing a subquery.

   **Expected result/shape:** For sql-start-03 Exercise 2, Three task rows, columns task_id, doubled_effort; final ORDER BY task_id: (2,10),(4,6),(5,6). The original same-level alias reference produces undefined_column, SQLSTATE 42703.

   **Verify:** For sql-start-03 Exercise 2, Inspect pairs (2,10),(4,6),(5,6), preserving both inclusive boundary values of 6. The original alias attempt reports undefined_column SQLSTATE 42703.

   **Progressive hint:** WHERE sees input columns; SELECT creates the alias later in the logical model.

3. **Repair Boolean grouping.**

   **Inputs/evidence:** For sql-start-03 Exercise 3, Return Red tasks whose status is open or blocked, with task_id, team, status. Diagnose the unparenthesized predicate team = 'Red' AND status = 'open' OR status = 'blocked'.

   **Expected result/shape:** For sql-start-03 Exercise 3, Two task rows with columns task_id, team, status; final ORDER BY task_id: IDs 1 and 5. The faulty predicate also returns Blue blocked task 6.

   **Verify:** For sql-start-03 Exercise 3, Trace Blue blocked task 6 through the faulty and repaired predicates. It appears only before grouping the status alternatives; the repaired IDs are 1,5.

   **Progressive hint:** Trace task 6 through each part of the original expression.

4. **Separate spelling from meaning.**

   **Inputs/evidence:** For sql-start-03 Exercise 4, Diagnose SELECT task_id, effrot FROM start_tasks and repair it to return task_id, effort for every task. State the error category before changing code.

   **Expected result/shape:** For sql-start-03 Exercise 4, Six rows with columns task_id, effort; final ORDER BY task_id. The misspelled input name produces undefined_column, SQLSTATE 42703; the corrected result includes ID 3 with NULL effort.

   **Verify:** For sql-start-03 Exercise 4, Capture undefined_column SQLSTATE 42703 for the misspelling in a separate attempted run, then inspect six corrected task identities and the retained NULL effort at ID 3.

   **Progressive hint:** Compare the requested column against the fixture declaration.

5. **Debug a threshold boundary.**

   **Inputs/evidence:** For sql-start-03 Exercise 5, Return open tasks with known effort at least 3, projecting task_id, effort. Explain the difference between >= 3 and > 3 on this fixture.

   **Expected result/shape:** For sql-start-03 Exercise 5, Two task rows, columns task_id, effort; final ORDER BY task_id: (4,3),(5,3). The strict > 3 version returns zero rows; missing effort does not qualify.

   **Verify:** For sql-start-03 Exercise 5, Require IDs 4 and 5 with effort 3. Independently try the strict comparison and observe zero qualifying open rows; closed ID 2 remains excluded in either case.

   **Progressive hint:** At least includes the boundary value itself.

6. **Combine a small reporting contract.**

   **Inputs/evidence:** For sql-start-03 Exercise 6, Return the first two open tasks ranked by largest effort, keeping unknown effort last, with task_id, team, effort. Explain every clause and its logical role.

   **Expected result/shape:** For sql-start-03 Exercise 6, Two task rows, columns task_id, team, effort; final ORDER BY effort DESC NULLS LAST, task_id: IDs 4 and 5, both effort 3. ID 3 is unknown, and closed task 2 is ineligible.

   **Verify:** For sql-start-03 Exercise 6, Compare final IDs 4,5 with the open-stage identities 1,3,4,5. Closed task 2 cannot enter despite its larger effort, and unknown task 3 cannot rank first.

   **Progressive hint:** Filter eligibility before defining the ranking and row limit.

## Self-check

- What evidence distinguishes a name error from a wrong business filter?
- Why can ORDER BY use doubled_effort while same-level WHERE cannot?
- Which fixture row catches the missing parentheses, and which rows catch the wrong threshold?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- An undefined-column error needs an identifier or scope investigation. Check the fixture columns and alias stage before changing installed software.

- A query that runs can still include task 6 incorrectly. Inspect a counterexample row to test Boolean grouping.

- After an unexpected error inside a transaction, later statements may report an aborted transaction. Fix the first error and rerun the complete file; do not treat later messages as independent root causes.

## Next step

Continue to historical `sql-01` with a deliberate input, filter, projection, and order workflow.

Concrete next target: [SQL Day 1](../../postgres-60day/companion-guides/day01_select_where_orderby.md).

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-start-03: Query Construction and Debugging using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_start_03_query_debugging.md
Answer-free learner: sql/professional/lessons/sql_start_03_query_debugging.sql
Direct prerequisite boundary: sql-start-02.
Teach at the foundation level, defining each new term before relying on it.
Focus on Build a query one clause at a time and inspect surviving identities. Separate parser/name errors from a syntactically valid wrong answer.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Whole SQL lesson (psql) and its ignored .learning/sql/sql-start-03/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
