# SQL-START-01: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_start_01_tables_and_grain.md)
and [learner script](../lessons/sql_start_01_tables_and_grain.sql). The separate
[executable solution](sql_start_01_tables_and_grain_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_start_01_tables_and_grain_solutions.sql`.
It uses only temporary fixtures, starts a transaction, and ends in rollback.
It must exit 0 with no contract failures. Each answer has a savepoint so an
experiment cannot silently change a later exercise's starting conditions.
The assertion helper treats false and unknown as failures, rather than allowing
a NULL assertion to pass accidentally. Keep the original fixture unchanged
when comparing your work so the stated identities remain a reliable oracle.

The code below is the answer for each numbered prompt, followed by its
reasoning. Inspect the first discrepancy in your own transcript before reading
a different answer. A solution is one defensible implementation of this contract;
an alternative is valid if its identities, values, missingness, ordering, and
transaction behavior match. Tests constrain the actual returned relation,
rather than assuming a familiar-looking query must be right.

## Exercise solutions

## Exercise 1: Trace identities

```sql
SELECT reading_id, station, temperature FROM start_readings ORDER BY reading_id;
```

The source contains six independent observations. SELECT chooses three attributes from each one, and ORDER BY uses the unique identity rather than physical insertion order. The two North rows at 18 remain separate observations. Do not add DISTINCT to make the display look shorter: that would answer a different question. A result that omits ID 4 silently loses a real observation just because its measurement is unknown. Compare each returned ID with the fixture before inspecting temperatures. The assertion checks the complete ID list, which detects both a missing observation and a repeated one.

**Inputs/evidence:** For sql-start-01 Exercise 1, Return all observations with reading_id, station, and temperature. Write a sentence naming the table grain and output grain before running the query. Use the identity as the final display order.

**Expected result/shape:** For sql-start-01 Exercise 1, Six rows, one per reading_id, with columns reading_id, station, temperature; final ORDER BY reading_id. IDs are 1,2,3,4,5,6 and ID 4 keeps its NULL measurement.

**Verify:** For sql-start-01 Exercise 1, Compare the six returned reading_id values with the fixture IDs 1 through 6 and inspect the NULL temperature at ID 4; no identity is repeated or absent.

## Exercise 2: Reveal repeated visible values

```sql
SELECT reading_id, station, reading_day, temperature FROM start_readings WHERE reading_id <= 2 ORDER BY reading_id;
```

WHERE restricts the candidate observations before projection. The output remains one row per reading_id, so the dates and identities expose two different facts even though station and temperature repeat. Deduplicating the visible measurement pair would merge two observations and destroy information. Keep identity columns visible while debugging, then hide them only when the presentation actually requires it. The check verifies both identities and their repeated measurement. It is possible for a table to have a sound primary key and for a particular projection to show duplicates; those statements describe different things.

**Inputs/evidence:** For sql-start-01 Exercise 2, Show reading_id, station, reading_day, temperature for IDs 1 and 2. Explain why projecting only station and temperature produces two identical-looking rows rather than one row.

**Expected result/shape:** For sql-start-01 Exercise 2, Two observation rows with columns reading_id, station, reading_day, temperature; final ORDER BY reading_id. Both temperatures are 18, with dates January 1 and January 2 respectively.

**Verify:** For sql-start-01 Exercise 2, Inspect two different reading_id and reading_day values while confirming both station/temperature pairs are North/18. Removing the visible identity must not collapse the two observations.

## Exercise 3: Filter observations without losing missing values

```sql
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'South' ORDER BY reading_id;
```

The predicate asks whether the station value equals South. It does not ask whether a measurement is present, positive, or usable. Consequently, both South observations survive: one records a known zero, and one records an unknown measurement. Adding temperature > 0 would introduce a new business requirement and remove both rows. Check returned identities before deciding that a short result is sensible. The verification counts two rows and separately checks that exactly one measurement is missing. This keeps a missing field distinct from an absent row, a difference that later outer joins also depend on.

**Inputs/evidence:** For sql-start-01 Exercise 3, Return the South observations with reading_id, station, temperature, ordered by reading_id. Do not add a measurement condition.

**Expected result/shape:** For sql-start-01 Exercise 3, Two rows keyed by reading_id, columns reading_id, station, temperature, final ORDER BY reading_id: (3, South, 0), (4, South, NULL).

**Verify:** For sql-start-01 Exercise 3, Inspect the two returned rows: reading_id 3 and 4, exactly one present zero temperature, and exactly one NULL measurement. Neither a missing field nor zero makes the South observation disappear.

## Exercise 4: Calculate without editing storage

```sql
SELECT reading_id, temperature, temperature + 2 AS adjusted_temperature FROM start_readings WHERE reading_id IN (1,3) ORDER BY reading_id;
```

SELECT evaluates the addition for each chosen observation and assigns a label to the resulting column. AS changes the displayed heading, not the table definition. IN is a short membership test for the two explicit IDs. The table values remain 18 and 0 because no UPDATE statement is present. The assertion checks the calculated sequence as well as the original fixture values. This distinguishes a successful calculation from a destructive workaround in which the learner edits the source to make the display match. Retain numeric types so addition is arithmetic, rather than building strings that merely look like numbers.

**Inputs/evidence:** For sql-start-01 Exercise 4, For IDs 1 and 3, return reading_id, temperature, and temperature + 2 named adjusted_temperature. Then rerun the original projection to show that the stored values did not change.

**Expected result/shape:** For sql-start-01 Exercise 4, Two rows keyed by reading_id, columns reading_id, temperature, adjusted_temperature, final ORDER BY reading_id: (1,18,20) and (3,0,2). Original temperatures remain 18 and 0.

**Verify:** For sql-start-01 Exercise 4, Inspect calculated values 20 and 2, then rerun the original reading_id/temperature projection and confirm the stored temperatures remain 18 and 0.

## Exercise 5: Distinguish no rows from a missing field

```sql
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'East' ORDER BY reading_id;
```

An empty result is a successful query with no matching observations. It is different from the South observation whose temperature is missing: that observation has an identity and other fields. The database cannot infer an East observation merely because someone asks for it. Do not manufacture a row containing zero or NULL unless the reporting contract explicitly requires a complete station list. The check tests cardinality directly instead of testing a temperature value that does not exist. In psql the column headings still appear above the zero-row message, showing that the output schema exists even when the result has no rows.

**Inputs/evidence:** For sql-start-01 Exercise 5, Search for station East and project reading_id, station, temperature. Compare its output with the South result from Exercise 3.

**Expected result/shape:** For sql-start-01 Exercise 5, Zero observation rows with columns reading_id, station, temperature and final ORDER BY reading_id. South has two rows, including a row with a NULL field; East has no stored observation.

**Verify:** For sql-start-01 Exercise 5, Inspect the zero-row message and compare it with the South row at ID 4, which has an identity and a NULL field. Do not manufacture an East row.

## Exercise 6: Transfer grain to a new collection

```sql
SELECT ticket_id, station, issue FROM (VALUES (11, 'North', 'battery'), (12, 'North', 'screen')) AS tickets(ticket_id, station, issue) ORDER BY ticket_id;
```

VALUES supplies a tiny input collection directly inside the query. The alias tickets names that collection, and its parentheses assign column names in the same order as the supplied fields. The technique makes a new example runnable without changing permanent tables. Both tickets happen at North, so station repeats while ticket_id distinguishes the facts. Reusing the earlier observation grain would be a conceptual error even though the SQL might run. The assertion verifies that the transfer retained both tickets and their common station. State the new grain aloud before checking the syntax: the identity follows the fact being modeled, not a familiar column name.

**Inputs/evidence:** For sql-start-01 Exercise 6, Use a VALUES input containing (11, 'North', 'battery') and (12, 'North', 'screen') with columns ticket_id, station, issue. Return ticket_id, station, issue ordered by ticket_id. Explain why station is not a ticket key.

**Expected result/shape:** For sql-start-01 Exercise 6, Two ticket rows, columns ticket_id, station, issue, final ORDER BY ticket_id: IDs 11 and 12 both belong to North. The output grain is one ticket, not one station or observation.

**Verify:** For sql-start-01 Exercise 6, Count two distinct ticket_id values and one distinct station; inspect battery at ID 11 and screen at ID 12 to retain their source associations.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
