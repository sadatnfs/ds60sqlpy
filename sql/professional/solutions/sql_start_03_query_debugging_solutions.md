# SQL-START-03: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_start_03_query_debugging.md)
and [learner script](../lessons/sql_start_03_query_debugging.sql). The separate
[executable solution](sql_start_03_query_debugging_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_start_03_query_debugging_solutions.sql`.
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

## Exercise 1: Build a checkpoint

```sql
SELECT task_id, team, status, effort FROM start_tasks WHERE team = 'Red' AND status = 'open' ORDER BY task_id;
```

The team filter leaves three candidate tasks, then the status condition removes the closed task 2. Writing both restrictions in one WHERE does not remove the value of reasoning through them separately. Both returned tasks belong to Red and remain open, and their efforts are 2 and 3. The verification checks exact task identities rather than only the row count, because two incorrect rows could satisfy a count of two. Keep intermediate predictions in your own notes. If the final list differs, inspect the first filter by itself before adding more conditions or changing the projection.

**Inputs/evidence:** For sql-start-03 Exercise 1, Return Red open tasks with task_id, team, status, effort. First predict all Red IDs and then the IDs remaining after the open restriction.

**Expected result/shape:** For sql-start-03 Exercise 1, Two task rows with columns task_id, team, status, effort; final ORDER BY task_id: IDs 1 and 5. The Red-only checkpoint has IDs 1,2,5.

**Verify:** For sql-start-03 Exercise 1, Inspect the Red-only stage IDs 1,2,5, then confirm only 1,5 remain after the status filter. Task 2 is the closed negative control.

## Exercise 2: Repair alias scope

```sql
SELECT task_id, effort * 2 AS doubled_effort FROM start_tasks WHERE effort * 2 >= 6 ORDER BY task_id;
```

Repeating the arithmetic keeps the predicate within the names available from FROM. SELECT then exposes the derived heading for presentation. The original error is a name-resolution problem, not evidence that the expression or threshold is invalid. IDs 4 and 5 sit exactly at the doubled threshold and must remain because the comparison is inclusive. The missing effort does not qualify. The assertion verifies both the identities and calculated values; fixing the error alone would be insufficient if the repair accidentally changed >= to >. A later lesson will introduce an intermediate query when repeating a longer expression becomes difficult to maintain.

**Inputs/evidence:** For sql-start-03 Exercise 2, Repair SELECT task_id, effort * 2 AS doubled_effort FROM start_tasks WHERE doubled_effort >= 6. Return task_id, doubled_effort in ascending task_id order without introducing a subquery.

**Expected result/shape:** For sql-start-03 Exercise 2, Three task rows, columns task_id, doubled_effort; final ORDER BY task_id: (2,10),(4,6),(5,6). The original same-level alias reference produces undefined_column, SQLSTATE 42703.

**Verify:** For sql-start-03 Exercise 2, Inspect pairs (2,10),(4,6),(5,6), preserving both inclusive boundary values of 6. The original alias attempt reports undefined_column SQLSTATE 42703.

## Exercise 3: Repair Boolean grouping

```sql
SELECT task_id, team, status FROM start_tasks WHERE team = 'Red' AND (status = 'open' OR status = 'blocked') ORDER BY task_id;
```

The parentheses make the status alternatives one unit that is combined with the team requirement. Under SQL precedence the original means either a Red open task or any blocked task, so task 6 slips in despite its Blue team. This is a semantic error because PostgreSQL can parse and execute the original successfully. Use a row that differs on the team boundary as a negative control. The assertion requires precisely tasks 1 and 5; merely testing that at least one Red open task appears would fail to catch the extra Blue result. Parentheses document the question and make later edits easier to review.

**Inputs/evidence:** For sql-start-03 Exercise 3, Return Red tasks whose status is open or blocked, with task_id, team, status. Diagnose the unparenthesized predicate team = 'Red' AND status = 'open' OR status = 'blocked'.

**Expected result/shape:** For sql-start-03 Exercise 3, Two task rows with columns task_id, team, status; final ORDER BY task_id: IDs 1 and 5. The faulty predicate also returns Blue blocked task 6.

**Verify:** For sql-start-03 Exercise 3, Trace Blue blocked task 6 through the faulty and repaired predicates. It appears only before grouping the status alternatives; the repaired IDs are 1,5.

## Exercise 4: Separate spelling from meaning

```sql
SELECT task_id, effort FROM start_tasks ORDER BY task_id;
```

The table defines effort, so effrot cannot be resolved as an input column. The correct repair changes the identifier, not the data or the environment. Quoting the misspelling would still name a nonexistent column. Once repaired, no WHERE clause should be invented: the question asks for every task. The assertion checks all six IDs and the count of present measurements, so accidentally filtering unknown effort is visible. In a real psql transcript the first error provides the code and position; capture that evidence instead of summarizing the whole run as broken. Re-execute the complete file after fixing the first error so transaction state is clean.

**Inputs/evidence:** For sql-start-03 Exercise 4, Diagnose SELECT task_id, effrot FROM start_tasks and repair it to return task_id, effort for every task. State the error category before changing code.

**Expected result/shape:** For sql-start-03 Exercise 4, Six rows with columns task_id, effort; final ORDER BY task_id. The misspelled input name produces undefined_column, SQLSTATE 42703; the corrected result includes ID 3 with NULL effort.

**Verify:** For sql-start-03 Exercise 4, Capture undefined_column SQLSTATE 42703 for the misspelling in a separate attempted run, then inspect six corrected task identities and the retained NULL effort at ID 3.

## Exercise 5: Debug a threshold boundary

```sql
SELECT task_id, effort FROM start_tasks WHERE status = 'open' AND effort >= 3 ORDER BY task_id;
```

The phrase at least translates to an inclusive comparison. The fixture deliberately places two open tasks exactly at 3, so a strict comparison fails visibly. The closed task with effort 5 is excluded by status even though its effort is high enough. The missing open effort produces unknown and is excluded by the measurement comparison, without any special zero replacement. The assertion tests the exact identities and values, which catches both a threshold error and forgetting the status filter. This kind of boundary fixture is usually more informative than adding dozens of ordinary rows that all satisfy both the correct and incorrect predicates.

**Inputs/evidence:** For sql-start-03 Exercise 5, Return open tasks with known effort at least 3, projecting task_id, effort. Explain the difference between >= 3 and > 3 on this fixture.

**Expected result/shape:** For sql-start-03 Exercise 5, Two task rows, columns task_id, effort; final ORDER BY task_id: (4,3),(5,3). The strict > 3 version returns zero rows; missing effort does not qualify.

**Verify:** For sql-start-03 Exercise 5, Require IDs 4 and 5 with effort 3. Independently try the strict comparison and observe zero qualifying open rows; closed ID 2 remains excluded in either case.

## Exercise 6: Combine a small reporting contract

```sql
SELECT task_id, team, effort FROM start_tasks WHERE status = 'open' ORDER BY effort DESC NULLS LAST, task_id LIMIT 2;
```

FROM introduces tasks, WHERE keeps only open ones, SELECT chooses three output fields, ORDER BY defines a complete ranking, and LIMIT takes the first two. The largest effort anywhere in the table belongs to closed task 2, so ranking the whole table before applying eligibility would answer the wrong question. Unknown effort is explicitly placed last. Task_id resolves the tie between tasks 4 and 5. The assertion verifies the selected identities in their final ranking order. Finish by explaining the query without reading it back word for word: one open task per row, sorted by known effort with an identity tie-breaker, capped at two.

**Inputs/evidence:** For sql-start-03 Exercise 6, Return the first two open tasks ranked by largest effort, keeping unknown effort last, with task_id, team, effort. Explain every clause and its logical role.

**Expected result/shape:** For sql-start-03 Exercise 6, Two task rows, columns task_id, team, effort; final ORDER BY effort DESC NULLS LAST, task_id: IDs 4 and 5, both effort 3. ID 3 is unknown, and closed task 2 is ineligible.

**Verify:** For sql-start-03 Exercise 6, Compare final IDs 4,5 with the open-stage identities 1,3,4,5. Closed task 2 cannot enter despite its larger effort, and unknown task 3 cannot rank first.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
