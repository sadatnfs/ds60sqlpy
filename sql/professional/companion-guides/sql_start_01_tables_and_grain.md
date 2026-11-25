# SQL-START-01: Reading Tables and Result Grain

## How to run this lesson

Start **sql-start-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. This lesson needs no course tables and
nothing from an earlier lesson: the script opens a transaction in the
disposable `advanced_sql_training` database, builds the six-row
`start_readings` temporary table, and ends with `ROLLBACK`, so every run starts
from the same six observations. Write your attempts in the saved copy at
`.learning/sql/sql-start-01/lesson/workspace/sql/professional/lessons/sql_start_01_tables_and_grain.sql`,
above that final `ROLLBACK`. A healthy psql transcript shows the setup tags
(`BEGIN`, `DO`, `SET`, `CREATE TABLE`, `INSERT 0 6`), then six rows for
Example 1, two rows for Example 2, your own result sets, and `ROLLBACK`. A lone
query pasted into **SQL snippet** runs on a new connection and fails with
`relation "start_readings" does not exist`, because a temporary table is
visible only to the session that created it.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-start-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** foundation
- **Direct catalog prerequisites:** None. Start here if you have never queried a database.
- **Artifacts:** [learner SQL](../lessons/sql_start_01_tables_and_grain.sql), [solution reasoning](../solutions/sql_start_01_tables_and_grain_solutions.md), [executable solution](../solutions/sql_start_01_tables_and_grain_solutions.sql).

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

A `VALUES` list builds a small table inside one query, with no
`CREATE TABLE` at all:

```sql
SELECT
  v.n,
  v.label
FROM (
  VALUES (1, 'a'),
    (2, 'b')) AS v (n, label)
ORDER BY
  v.n;
```

Each parenthesized group is one row. `AS v` names the derived table, and the
column list `(n, label)` names its columns in order, so `v.n` and `v.label` can
be selected and sorted. Without that list PostgreSQL calls the columns
`column1` and `column2`. The query returns two rows, `(1, a)` and `(2, b)`.
Exercise 6 uses the same form for a new collection.

## Worked example / walkthrough

Both examples read the same six `start_readings` rows. Before running each
one, write how many rows it will print and which `reading_id` values they come
from. Example 2 is where that prediction usually goes wrong: it hides the
identity column, so you must reason from the `WHERE reading_id <= 2` filter
rather than from what the screen shows.

### Example 1: A full observation retains its identity

```sql
SELECT
  reading_id,
  station,
  reading_day,
  temperature
FROM
  start_readings
ORDER BY
  reading_id;
```

The input and output grain are both one observation, identified by reading_id. Selecting four columns changes the width of the result, not the number of observations. The missing South measurement is printed as an empty-looking field by default in psql; it is the SQL NULL marker, not a zero. Use the explicit ID to locate that observation.

**Expected:** Six rows with columns reading_id, station, reading_day, temperature; IDs 1 through 6 in order. ID 4 has NULL temperature.

### Example 2: Two visually identical rows are still two observations

```sql
SELECT
  station,
  temperature
FROM
  start_readings
WHERE
  reading_id <= 2
ORDER BY
  reading_id;
```

FROM starts with six observations; WHERE keeps IDs 1 and 2; SELECT hides their IDs and dates. Both output rows now display North and 18. SQL preserves both rows. The input identities explain why the repeated visible values are valid. Rerun with reading_id in the SELECT list to make the distinction visible. Sorting by an unprojected input column is allowed here because this is an ordinary SELECT without DISTINCT.

**Expected:** Two rows, each (North, 18), with columns station and temperature. No table row is removed or updated.

## Exercises

Exercises 1 to 5 query `start_readings`; Exercise 6 builds its own `VALUES`
collection. Before each query, finish the sentence "One output row represents
..." and check it against the Expected line. Exercises 3 and 5 are a pair:
both filter on `station`, but South returns a row whose temperature is NULL
while East returns no row at all, and your explanation should keep those two
outcomes apart. The contract lines work as described in the
[study guide](../../STUDY-GUIDE.md#work-an-exercise).

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

For retrieval practice, explain without the code why
`SELECT DISTINCT station, temperature FROM start_readings` returns five rows
instead of six (IDs 1 and 2 collapse into one North/18 row), and why adding
`AND temperature > 0` to Exercise 3 would remove both South observations, the
known zero at ID 3 and the unknown value at ID 4.

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
