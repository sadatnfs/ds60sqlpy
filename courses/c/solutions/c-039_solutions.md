# c-039: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Memory access patterns can dominate arithmetic cost. An array of structs keeps each record together; a struct of arrays keeps one field across many records contiguous. Which layout is better depends on the operations performed, not a universal rule. Padding, alignment, cache lines and compiler vectorization influence observed performance. Begin with equivalent results and operation counts, then measure representative workloads under controlled builds. Do not publish a speedup based on one tiny timing or assume a particular cache-line size from a diagram. Optimization must preserve bounds, aliasing and numerical contracts.

sizeof reports actual object size including padding. offsetof gives a field offset without dereferencing a null pointer. Iterate only over initialized logical elements. restrict can promise nonaliasing to the compiler, but violating that promise is a correctness defect; it is not a harmless performance hint. The fixture compares layouts semantically and intentionally makes no wall-clock threshold assertion.

## Exercise 1: Sum one field in records

Sum x fields from three Point records.

```c
struct Point records[] = {{1, 10}, {2, 20}, {3, 30}};
int sum = 0;
for (size_t i = 0; i < 3; i++)
  sum += records[i].x;
CHECK(sum == 6);
```

**Expected:** The result is 6.

This traversal touches a selected field in each record. Whether unused fields waste bandwidth depends on the real layout and workload.

## Exercise 2: Compute the same result by columns

Sum an x column containing 1, 2, 3.

```c
int x[] = {1, 2, 3};
int y[] = {10, 20, 30};
int sum = 0;
for (size_t i = 0; i < 3; i++)
  sum += x[i];
CHECK(sum == 6 && y[2] == 30);
```

**Expected:** The result is also 6.

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

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
