# c-042: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

The capstone combines parsing, range checks, bounded storage, deterministic aggregation and failure-atomic output. A production C component is understandable when each boundary states its grammar, ownership, resource limit and failure behavior. This fixture accepts a narrow line format name,count with one comma, a short nonempty ASCII name and a nonnegative decimal count. It deliberately rejects quoting and multiline fields rather than pretending to implement full CSV. A real general-purpose CSV reader needs the richer format contract. The pipeline validates every record before committing its summary, so one malformed record cannot publish a partial total as if the batch completed.

parse_record separates a bounded name from a complete decimal value using strtol and an end pointer. summarize stages row count and total, checks addition before updating, and commits only when every row is valid. The output remains unchanged on failure. The separately prepared stats project illustrates headers and tests; this capstone keeps its full deterministic data path within the ordinary one-file pad.

## Exercise 1: Summarize valid records

Process alpha,3 and beta,4.

```c
const char *rows[] = {"alpha,3", "beta,4"};
struct Summary out = {0};
CHECK(summarize(rows, 2, &out) && out.rows == 2 && out.total == 7);
```

**Expected:** Two rows produce total 7.

The total represents the complete accepted batch, not merely a successful prefix.

## Exercise 2: Reject a malformed record

Process one valid record followed by a negative count.

```c
const char *rows[] = {"alpha,3", "beta,-1"};
struct Summary out = {9, 99};
CHECK(!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99);
```

**Expected:** The batch fails and the previous summary remains unchanged.

Staging prevents a partial total from masquerading as a successful batch result.

## Exercise 3: Handle an empty batch

Summarize zero records.

```c
struct Summary out = {9, 99};
CHECK(summarize(NULL, 0, &out) && out.rows == 0 && out.total == 0);
```

**Expected:** Rows and total are both zero.

The empty input has an explicit identity result. No record pointer is accessed.

## Exercise 4: Reject extra field syntax

Parse a line with two commas.

```c
unsigned value = 0;
CHECK(!parse_record("alpha,3,extra", &value));
```

**Expected:** The record is rejected.

The accepted grammar is intentionally narrow. Extra fields must not be silently ignored.

## Exercise 5: Preserve a legitimate zero

Process alpha,0.

```c
const char *rows[] = {"alpha,0"};
struct Summary out = {0};
CHECK(summarize(rows, 1, &out) && out.rows == 1 && out.total == 0);
```

**Expected:** One row contributes zero to the total.

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

The failed attempt leaves no hidden partial state. Re-running corrected input is safe under this pure in-memory batch contract.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
