# SQL-START-01: Reading Tables and Result Grain

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-start-01**. The
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
   `.learning/sql/sql-start-01/lesson/workspace/sql/professional/lessons/sql_start_01_tables_and_grain.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-start-01
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
- **Direct catalog prerequisites:** None. Start here if you have never queried a database.
- **Artifacts:** [learner SQL](../lessons/sql_start_01_tables_and_grain.sql), [solution reasoning](../solutions/sql_start_01_tables_and_grain_solutions.md), [executable solution](../solutions/sql_start_01_tables_and_grain_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Identify the fact represented by a row before writing a query.
- Keep an identity column visible while checking a projection or filter.
- Explain why a result set can contain repeated visible values without duplicate observations.

## Vocabulary and concepts

A spreadsheet gives cells a visible position. A database table gives facts named
columns and an identity. Its storage position is not a promised presentation
order. Imagine a weather observer recording a station once each day. The fact
is an observation, not a station: North can occur on several different days.
The fixture has six observations and three stations. Two North observations
happen to have the same temperature. Removing the observation identity from a
query makes those rows look alike; it does not make one of them a mistake.



- **Table:** A table is a collection of rows with the same named columns and declared
types. 

- **Row:** A row represents one fact at a stated level of detail. 

- **Grain:** Grain is
that level of detail, such as one observation identified by `reading_id`.


- **Column:** A column is one attribute of every row, such as `station` or `temperature`.


- **Primary key:** A primary key is a column or column combination that uniquely identifies
each table row and cannot be missing. 

- **Result set:** A result set is the rows and columns
returned by a query; displaying it does not create another stored table.


- **Projection:** A projection chooses output columns and expressions. It normally keeps
the number of input rows unless another clause removes or combines them.

`reading_id` identifies an observation. `station` does not, because the same
station can be observed repeatedly. A temperature is a measurement, never an
identity here. Always finish the sentence "One output row represents ..."
before selecting columns. If the sentence changes, decide whether the query
actually performs that change. Merely omitting `reading_id` changes what you
can see, not what the remaining rows represent.

## Syntax anatomy and query reasoning

Read `SELECT reading_id, station FROM start_readings ORDER BY reading_id;`
in three parts. `FROM start_readings` names the input collection. `SELECT`
names the output columns separated by commas. `ORDER BY reading_id` makes
the display order explicit. The semicolon terminates the statement; a line
break usually does not. SQL keywords are written in uppercase for readability,
but unquoted keyword case does not change the operation.

A string value such as `'North'` uses single quotes. `station` without quotes
refers to a column. `AS temperature_plus_two` gives a calculated column a
readable output heading; it does not rename the stored column. In
`temperature + 2`, the calculation happens separately for each selected row.
Add `WHERE station = 'South'` between `FROM` and `ORDER BY` to keep only
matching observations. Think input, filter, projection, display. This lesson
uses only this small part of SQL; joins, grouping, and windows come later.

The file prepares a temporary table for you. `CREATE TEMP TABLE` and `INSERT`
are fixture setup, not prerequisites you must reproduce from memory. The
surrounding `BEGIN` and `ROLLBACK` ensure the fixture disappears at the end.
When experimenting interactively, run setup and your queries in the same
connection, then run `ROLLBACK`. A new connection cannot see another
connection's temporary table.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: A full observation retains its identity

```sql
SELECT reading_id, station, reading_day, temperature
FROM start_readings
ORDER BY reading_id;
```

The input and output grain are both one observation, identified by reading_id. Selecting four columns changes the width of the result, not the number of observations. The missing South measurement is printed as an empty-looking field by default in psql; it is the SQL NULL marker, not a zero. Use the explicit ID to locate that observation.

**Expected:** Six rows with columns reading_id, station, reading_day, temperature; IDs 1 through 6 in order. ID 4 has NULL temperature.

### Example 2: Two visually identical rows are still two observations

```sql
SELECT station, temperature
FROM start_readings
WHERE reading_id <= 2
ORDER BY reading_id;
```

FROM starts with six observations; WHERE keeps IDs 1 and 2; SELECT hides their IDs and dates. Both output rows now display North and 18. SQL preserves both rows. The input identities explain why the repeated visible values are valid. Rerun with reading_id in the SELECT list to make the distinction visible. Sorting by an unprojected input column is allowed here because this is an ordinary SELECT without DISTINCT.

**Expected:** Two rows, each (North, 18), with columns station and temperature. No table row is removed or updated.

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Trace identities.**

   **Inputs/evidence:** For sql-start-01 Exercise 1, Return all observations with reading_id, station, and temperature. Write a sentence naming the table grain and output grain before running the query. Use the identity as the final display order.

   **Expected result/shape:** For sql-start-01 Exercise 1, Six rows, one per reading_id, with columns reading_id, station, temperature; final ORDER BY reading_id. IDs are 1,2,3,4,5,6 and ID 4 keeps its NULL measurement.

   **Verify:** For sql-start-01 Exercise 1, Compare the six returned reading_id values with the fixture IDs 1 through 6 and inspect the NULL temperature at ID 4; no identity is repeated or absent.

   **Progressive hint:** Start with FROM, then choose the three requested columns.

2. **Reveal repeated visible values.**

   **Inputs/evidence:** For sql-start-01 Exercise 2, Show reading_id, station, reading_day, temperature for IDs 1 and 2. Explain why projecting only station and temperature produces two identical-looking rows rather than one row.

   **Expected result/shape:** For sql-start-01 Exercise 2, Two observation rows with columns reading_id, station, reading_day, temperature; final ORDER BY reading_id. Both temperatures are 18, with dates January 1 and January 2 respectively.

   **Verify:** For sql-start-01 Exercise 2, Inspect two different reading_id and reading_day values while confirming both station/temperature pairs are North/18. Removing the visible identity must not collapse the two observations.

   **Progressive hint:** A column can repeat even when the primary key cannot.

3. **Filter observations without losing missing values.**

   **Inputs/evidence:** For sql-start-01 Exercise 3, Return the South observations with reading_id, station, temperature, ordered by reading_id. Do not add a measurement condition.

   **Expected result/shape:** For sql-start-01 Exercise 3, Two rows keyed by reading_id, columns reading_id, station, temperature, final ORDER BY reading_id: (3, South, 0), (4, South, NULL).

   **Verify:** For sql-start-01 Exercise 3, Inspect the two returned rows: reading_id 3 and 4, exactly one present zero temperature, and exactly one NULL measurement. Neither a missing field nor zero makes the South observation disappear.

   **Progressive hint:** The question restricts station, not temperature.

4. **Calculate without editing storage.**

   **Inputs/evidence:** For sql-start-01 Exercise 4, For IDs 1 and 3, return reading_id, temperature, and temperature + 2 named adjusted_temperature. Then rerun the original projection to show that the stored values did not change.

   **Expected result/shape:** For sql-start-01 Exercise 4, Two rows keyed by reading_id, columns reading_id, temperature, adjusted_temperature, final ORDER BY reading_id: (1,18,20) and (3,0,2). Original temperatures remain 18 and 0.

   **Verify:** For sql-start-01 Exercise 4, Inspect calculated values 20 and 2, then rerun the original reading_id/temperature projection and confirm the stored temperatures remain 18 and 0.

   **Progressive hint:** An expression in SELECT calculates a result; UPDATE would change storage.

5. **Distinguish no rows from a missing field.**

   **Inputs/evidence:** For sql-start-01 Exercise 5, Search for station East and project reading_id, station, temperature. Compare its output with the South result from Exercise 3.

   **Expected result/shape:** For sql-start-01 Exercise 5, Zero observation rows with columns reading_id, station, temperature and final ORDER BY reading_id. South has two rows, including a row with a NULL field; East has no stored observation.

   **Verify:** For sql-start-01 Exercise 5, Inspect the zero-row message and compare it with the South row at ID 4, which has an identity and a NULL field. Do not manufacture an East row.

   **Progressive hint:** A WHERE condition can produce an empty result without causing an error.

6. **Transfer grain to a new collection.**

   **Inputs/evidence:** For sql-start-01 Exercise 6, Use a VALUES input containing (11, 'North', 'battery') and (12, 'North', 'screen') with columns ticket_id, station, issue. Return ticket_id, station, issue ordered by ticket_id. Explain why station is not a ticket key.

   **Expected result/shape:** For sql-start-01 Exercise 6, Two ticket rows, columns ticket_id, station, issue, final ORDER BY ticket_id: IDs 11 and 12 both belong to North. The output grain is one ticket, not one station or observation.

   **Verify:** For sql-start-01 Exercise 6, Count two distinct ticket_id values and one distinct station; inspect battery at ID 11 and screen at ID 12 to retain their source associations.

   **Progressive hint:** Name the three VALUES columns in the table alias.

## Self-check

- Why can North appear three times in a sound observation table?
- What changes when a column is removed from SELECT, and what does not?
- How would you distinguish no matching station from one observation with an unknown temperature?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- Seeing two identical-looking rows does not prove duplicated source facts. Add reading_id and reading_day to the projection before considering deduplication.

- An empty psql field can represent NULL. Inspect reading_id 4 rather than replacing it with zero just to make the screen easier to read.

- A result appearing sorted once proves only that run. Add ORDER BY reading_id whenever the exercise promises an identity order.

## Next step

Continue to `sql-start-02` for values, missingness, truth, and ordering.

Concrete next target: [Values, NULL, and deterministic order](sql_start_02_values_null_order.md).

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-start-01: Reading Tables and Result Grain using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_start_01_tables_and_grain.md
Answer-free learner: sql/professional/lessons/sql_start_01_tables_and_grain.sql
Direct prerequisite boundary: none; assume no SQL knowledge.
Teach at the foundation level, defining each new term before relying on it.
Focus on Identify the fact represented by a row before writing a query. Keep an identity column visible while checking a projection or filter.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Whole SQL lesson (psql) and its ignored .learning/sql/sql-start-01/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
