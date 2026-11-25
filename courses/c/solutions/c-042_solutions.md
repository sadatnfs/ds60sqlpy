# c-042: explained solutions

`c-042_solution.c` assembles the "summarize valid records" case through the "transfer repeatable recovery" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

The capstone combines parsing, range checks, bounded storage, deterministic aggregation and failure-atomic output. A production C component is understandable when each boundary states its grammar, ownership, resource limit and failure behavior. This fixture accepts a narrow line format `name,count` with one comma, a short nonempty ASCII name and a nonnegative decimal count. It deliberately rejects quoting and multiline fields rather than pretending to implement full CSV. A real general-purpose CSV reader needs the richer format contract. The pipeline validates every record before committing its summary, so one malformed record cannot publish a partial total as if the batch completed.

parse_record separates a bounded name from a complete decimal value using strtol and an end pointer. summarize stages row count and total, checks addition before updating, and commits only when every row is valid. The output remains unchanged on failure. The separately prepared stats project illustrates headers and tests; this capstone keeps its full deterministic data path within the ordinary one-file pad.

## Exercise 1: Summarize valid records: change one input

In worked example 1, change `const char *rows[] = {"alpha,3", "beta,4"};` to `const char *rows[] = {"alpha,4", "beta,4"};`. Predict which value the CHECK on `summarize(rows, 2, &out) && out.rows == 2 && out.total == 7` sees, then run and restore.

The unchanged code is worked example 1:

```c
const char *rows[] = {"alpha,3", "beta,4"};
struct Summary out = {0};
CHECK(summarize(rows, 2, &out) && out.rows == 2 && out.total == 7);
```

**Expected:** `Check failed` at `summarize(rows, 2, &out) && out.rows == 2 && out.total == 7`; restoring `const char *rows[] = {"alpha,3", "beta,4"};` passes again.

**Verify:** Name the value that made `summarize(rows, 2, &out) && out.rows == 2 && out.total == 7` false, where worked example 1 showed that two rows produce total 7.

The total represents the complete accepted batch, not merely a successful prefix.

## Exercise 2: Reject a malformed record: debug a regression

Worked example 2 now has a line reading `struct Summary out = {10, 99};`. Repair it so that the batch fails and the previous summary remains unchanged again.

The unchanged code is worked example 2:

```c
const char *rows[] = {"alpha,3", "beta,-1"};
struct Summary out = {9, 99};
CHECK(!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99);
```

**Expected:** `Check failed` at `!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99` until the line reads `struct Summary out = {9, 99};` again.

**Verify:** Explain how `struct Summary out = {10, 99};` changes the value `!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99` tests, using your failing and repaired runs.

Staging prevents a partial total from masquerading as a successful batch result.

## Exercise 3: Handle an empty batch

Summarize zero records.

```c
struct Summary out = {9, 99};
CHECK(summarize(NULL, 0, &out) && out.rows == 0 && out.total == 0);
```

**Expected:** Rows and total are both zero.

**Verify:** Keep a CHECK equivalent to `summarize(NULL, 0, &out) && out.rows == 0 && out.total == 0`. Control edit: `CHECK(summarize(NULL, 1, &out) && out.rows == 0 && out.total == 0);` must fail; then restore it.

The empty input has an explicit identity result. No record pointer is accessed.

## Exercise 4: Reject extra field syntax

Parse a line with two commas.

```c
unsigned value = 0;
CHECK(!parse_record("alpha,3,extra", &value));
```

**Expected:** The record is rejected.

**Verify:** Keep a CHECK equivalent to `!parse_record("alpha,3,extra", &value)`. Control edit: `CHECK(parse_record("alpha,3,extra", &value));` must fail; then restore it.

The accepted grammar is intentionally narrow. Extra fields must not be silently ignored.

## Exercise 5: Preserve a legitimate zero

Process alpha,0.

```c
const char *rows[] = {"alpha,0"};
struct Summary out = {0};
CHECK(summarize(rows, 1, &out) && out.rows == 1 && out.total == 0);
```

**Expected:** One row contributes zero to the total.

**Verify:** Keep a CHECK equivalent to `summarize(rows, 1, &out) && out.rows == 1 && out.total == 0`. Control edit: changing `const char *rows[] = {"alpha,0"};` to `const char *rows[] = {"alpha,1"};` must fail it; then restore it.

A zero measurement differs from missing or invalid input, and row count retains that distinction.

## Exercise 6: Transfer repeatable recovery

Fail one batch, then run a corrected batch against the same output.

```c
const char *bad[] = {"x,bad"}, *good[] = {"x,8"};
struct Summary out = {0};
CHECK(!summarize(bad, 1, &out));
CHECK(summarize(good, 1, &out) && out.rows == 1 && out.total == 8);
```

**Expected:** Only the corrected complete batch publishes total 8.

**Verify:** Keep a CHECK equivalent to `summarize(good, 1, &out) && out.rows == 1 && out.total == 8`. Control edit: changing `const char *bad[] = {"x,bad"}, *good[] = {"x,8"};` to `const char *bad[] = {"x,bad"}, *good[] = {"x,9"};` must fail it; then restore it.

The failed attempt leaves no hidden partial state. Re-running corrected input is safe under this pure in-memory batch contract.

## After comparison

Summarize `{"a,4294967295", "b,1"}`: each record parses, but the running total would exceed `UINT_MAX`. CHECK that `summarize` fails and that an `out` already holding one row and total 8 is unchanged. Then explain why the test `value > UINT_MAX - staged.total` must come before the addition, and why staging in `staged` keeps the failed batch invisible.
