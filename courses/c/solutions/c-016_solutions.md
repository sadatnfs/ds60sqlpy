# c-016: explained solutions

`c-016_solution.c` assembles the "push into an empty vector" case through the "transfer reserve failure atomicity" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A dynamic vector separates logical length from allocated capacity. Growth may move the allocation, invalidating prior element pointers. realloc returns a new pointer on success; on failure for a nonzero requested size, the original allocation remains owned and unchanged. Assigning realloc directly to the only owning pointer can therefore lose the original allocation on failure. Keep the result in a temporary, validate it, then update the vector. Growth arithmetic needs overflow checks and a resource policy. The vector here owns ints and preserves its old state when a reserve request is rejected.

A vector stores data, len and cap. reserve ensures capacity without changing length. push reserves before writing data[len], then increments length. pop checks nonempty before decrementing. destroy frees storage and resets all fields, making repeated cleanup harmless under this local ownership contract. Never retain an element pointer across a call that may grow the vector.

## Exercise 1: Push into an empty vector: predict an edited check

In worked example 1, change `CHECK(vector_push(&v, 3) && vector_push(&v, 5));` to `CHECK(vector_push(&v, 4) && vector_push(&v, 5));`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
struct Vector v = {0};
CHECK(vector_push(&v, 3) && vector_push(&v, 5));
CHECK(v.len == 2 && v.data[0] == 3 && v.data[1] == 5);
vector_destroy(&v);
```

**Expected:** `Check failed`: `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` is false, although length is 2 and values are retained.

**Verify:** Explain which claim `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` makes that the state fails; restoring `CHECK(vector_push(&v, 3) && vector_push(&v, 5));` passes again.

The zero state is a usable empty vector. Growth happens before the first write.

## Exercise 2: Reserve without adding elements: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(v.cap > 8 && v.len == 0);`. Explain why it fails although capacity is at least eight while length stays zero, then restore it.

The unchanged code is worked example 2:

```c
struct Vector v = {0};
CHECK(vector_reserve(&v, 8));
CHECK(v.cap >= 8 && v.len == 0);
vector_destroy(&v);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(v.cap >= 8 && v.len == 0);` again, though capacity is at least eight while length stays zero.

**Verify:** Explain why `CHECK(v.cap > 8 && v.len == 0);` rejects a state that `v.cap >= 8 && v.len == 0` accepts, using your failing and repaired runs.

Reservation is storage preparation, not logical insertion. Treating capacity as length would expose uninitialized elements.

## Exercise 3: Grow while preserving contents

Push twenty sequential values.

```c
struct Vector v = {0};
for (int i = 0; i < 20; i++)
  CHECK(vector_push(&v, i));
for (size_t i = 0; i < v.len; i++)
  CHECK(v.data[i] == (int)i);
vector_destroy(&v);
```

**Expected:** Every stored value matches its index.

**Verify:** Keep a CHECK equivalent to `v.data[i] == (int)i`. Control edit: changing `for (size_t i = 0; i < v.len; i++)` to `for (size_t i = 0; i <= v.len; i++)` must fail it; then restore it.

Each successful growth preserves the previously initialized prefix. Old element pointers must not be used after a possible move.

## Exercise 4: Pop from a nonempty vector

Push 7 then pop it.

```c
struct Vector v = {0};
int out = 0;
CHECK(vector_push(&v, 7));
CHECK(vector_pop(&v, &out) && out == 7 && v.len == 0);
vector_destroy(&v);
```

**Expected:** The returned value is 7 and length becomes zero.

**Verify:** Keep a CHECK equivalent to `vector_pop(&v, &out) && out == 7 && v.len == 0`. Control edit: `CHECK(vector_push(&v, 8));` must fail; then restore it.

The vector retains capacity after removal, which can make later pushes cheap without changing the empty logical state.

## Exercise 5: Reject an empty pop

Pop an empty vector with an existing output value.

```c
struct Vector v = {0};
int out = 9;
CHECK(!vector_pop(&v, &out) && out == 9);
vector_destroy(&v);
```

**Expected:** The operation fails and output stays 9.

**Verify:** Keep a CHECK equivalent to `!vector_pop(&v, &out) && out == 9`. Control edit: changing `int out = 9;` to `int out = 10;` must fail it; then restore it.

The failure path performs no decrement and no out-of-bounds read.

## Exercise 6: Transfer reserve failure atomicity

Reject SIZE_MAX capacity after storing one item.

```c
struct Vector v = {0};
CHECK(vector_push(&v, 4));
CHECK(!vector_reserve(&v, SIZE_MAX));
CHECK(v.len == 1 && v.data[0] == 4);
vector_destroy(&v);
```

**Expected:** The original value and length remain intact.

**Verify:** Keep a CHECK equivalent to `v.len == 1 && v.data[0] == 4`. Control edit: `CHECK(vector_push(&v, 5));` must fail; then restore it.

Arithmetic rejection happens before realloc. This deterministic case tests state preservation without depending on host memory exhaustion.

## After comparison

Push 1 through 5 into an empty vector, record `cap`, then pop all five. CHECK that `vector_pop` writes 5, 4, 3, 2 and 1 through its output in that order, that `len` ends at 0 and that `cap` is unchanged. A sixth pop must return false and leave its output untouched. Then explain why a pointer saved to `data[0]` before the pushes may be stale afterward, even though `len` is back to 0.
