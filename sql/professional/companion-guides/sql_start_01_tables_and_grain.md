# SQL-START-01: Reading Tables and Result Grain

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **PostgreSQL** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use only the local disposable `advanced_sql_training` database on PostgreSQL
16 or newer. The lesson page is a readable preview. In the private course
portal, choose **Create/open guided SQL notebook**, run readiness, acknowledge
only the explicitly offered course reset if needed, and edit the notebook's
ignored `.learning/sql/sql-start-01/` SQL copy. Its exact path is
`.learning/sql/sql-start-01/lesson/workspace/sql/professional/lessons/sql_start_01_tables_and_grain.sql`. Save the copy and run its complete-script
cell. Output appears below that cell as a full `psql` transcript. A successful
run ends in `ROLLBACK`, exits 0, and has the example identities stated below.
The setup uses temporary tables and no external data or extension.

If using VS Code directly, run from the repository root. These fallbacks work
in terminals after PostgreSQL setup:

```powershell
# Windows PowerShell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_start_01_tables_and_grain.sql"
```

```bash
# macOS/Linux
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_start_01_tables_and_grain.sql
```

Keep `-X` to ignore personal client startup changes and `ON_ERROR_STOP` to
stop at the first unexpected error. If `psql` is missing, return to the
operating-system setup and `scripts/course.py doctor`. An authentication
failure needs the local setup workflow, never a password pasted into a lesson.
If the database-name guard rejects the run, inspect your target instead of
removing the guard. After an unexpected transaction error, fix that first
error and rerun the whole file in a fresh connection. To try an exercise, put
its SQL before the final `ROLLBACK` in your private copy; temporary tables
exist only in that connection and transaction. Running this official learner
file demonstrates the examples; exercises remain answer-free until you add an
attempt. Do not edit the separate official solutions while studying.

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
Prefer Create/open guided SQL notebook and its ignored .learning/sql/sql-start-01/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
