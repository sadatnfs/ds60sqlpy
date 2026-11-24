# c-039: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-039_solution.c`, implements all six cases, from the "sum one field in records" case to the "transfer a partial block" case, in one `main.c`.

## Mechanism and assumptions

Memory access patterns can dominate arithmetic cost. An array of structs keeps each record together; a struct of arrays keeps one field across many records contiguous. Which layout is better depends on the operations performed, not a universal rule. Padding, alignment, cache lines and compiler vectorization influence observed performance. Begin with equivalent results and operation counts, then measure representative workloads under controlled builds. Do not publish a speedup based on one tiny timing or assume a particular cache-line size from a diagram. Optimization must preserve bounds, aliasing and numerical contracts.

sizeof reports actual object size including padding. offsetof gives a field offset without dereferencing a null pointer. Iterate only over initialized logical elements. restrict can promise nonaliasing to the compiler, but violating that promise is a correctness defect; it is not a harmless performance hint. The fixture compares layouts semantically and intentionally makes no wall-clock threshold assertion.

## Exercise 1: Sum one field in records: change one input

Copy worked example 1, the "sum one field in records" case, into a scratch pad and change `struct Point records[] = {{1, 10}, {2, 20}, {3, 30}};` to `struct Point records[] = {{2, 10}, {2, 20}, {3, 30}};`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the result is 6); then run it and restore the original line.

The unchanged code is worked example 1:

```c
struct Point records[] = {{1, 10}, {2, 20}, {3, 30}};
int sum = 0;
for (size_t i = 0; i < 3; i++)
  sum += records[i].x;
CHECK(sum == 6);
```

**Expected:** With `struct Point records[] = {{2, 10}, {2, 20}, {3, 30}};` the run stops with `Check failed` at the CHECK on `sum == 6`, because the "sum one field in records" case no longer shows that the result is 6. Restoring `struct Point records[] = {{1, 10}, {2, 20}, {3, 30}};` brings that observation back.

This traversal touches a selected field in each record. Whether unused fields waste bandwidth depends on the real layout and workload.

## Exercise 2: Compute the same result by columns: debug a regression

A regression changed one token in worked example 2, the "compute the same result by columns" case, so one line now reads `sum -= x[i];`. Run the example with that line, use the failing CHECK to find why the result is also 6 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int x[] = {1, 2, 3};
int y[] = {10, 20, 30};
int sum = 0;
for (size_t i = 0; i < 3; i++)
  sum += x[i];
CHECK(sum == 6 && y[2] == 30);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `sum == 6 && y[2] == 30`. Once the line reads `sum += x[i];` again, the "compute the same result by columns" case again shows that the result is also 6.

Equivalent semantics must be established before comparing timings. The y column remains independent storage.

## Exercise 3: Inspect legal field offsets

Inspect x and y offsets in Point.

```c
CHECK(offsetof(struct Point, x) < sizeof(struct Point));
CHECK(offsetof(struct Point, y) > offsetof(struct Point, x));
```

**Expected:** Offsets are within the struct and preserve declaration order.

The check does not assume an exact padding count. Layout is an ABI property that may vary by implementation.

## Exercise 4: Count algorithmic work

Scan six values and count iterations.

```c
int values[] = {1, 2, 3, 4, 5, 6};
size_t visits = 0;
int sum = 0;
for (size_t i = 0; i < 6; i++) {
  visits++;
  sum += values[i];
}
CHECK(visits == 6 && sum == 21);
```

**Expected:** Exactly six visits occur.

Deterministic operation evidence is different from elapsed-time measurement, which needs repeated controlled experiments.

## Exercise 5: Preserve result under blocking

Sum the same data in blocks of two.

```c
int values[] = {1, 2, 3, 4, 5, 6};
int sum = 0;
for (size_t block = 0; block < 6; block += 2)
  for (size_t i = block; i < block + 2; i++)
    sum += values[i];
CHECK(sum == 21);
```

**Expected:** The total remains 21.

This toy blocking change preserves bounds exactly. Real blocked loops must handle a final partial block.

## Exercise 6: Transfer a partial block

Sum five values in blocks of two with a bounded final block.

```c
int values[] = {1, 2, 3, 4, 5};
int sum = 0;
for (size_t block = 0; block < 5; block += 2) {
  size_t end = block + 2;
  if (end > 5)
    end = 5;
  for (size_t i = block; i < end; i++)
    sum += values[i];
}
CHECK(sum == 15);
```

**Expected:** The total is 15 without a sixth access.

The incomplete final block is a correctness case that an optimization must retain. Timing only even-sized inputs would miss it.

## After comparison

Add a fresh distinguishing input for the "transfer a partial block" case to your own c-039 source. Explain why every access in the case code inside `main` stays within a live object and each owned resource is released. An expected locality failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "compute the same result by columns" case apart from ordinary output: the fixture proves its stated locality, array of structs and struct of arrays assumptions, not universal safety.
