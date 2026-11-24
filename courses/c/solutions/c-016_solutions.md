# c-016: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-016_solution.c`, implements all six cases, from the "push into an empty vector" case to the "transfer reserve failure atomicity" case, in one `main.c`.

## Mechanism and assumptions

A dynamic vector separates logical length from allocated capacity. Growth may move the allocation, invalidating prior element pointers. realloc returns a new pointer on success; on failure for a nonzero requested size, the original allocation remains owned and unchanged. Assigning realloc directly to the only owning pointer can therefore lose the original allocation on failure. Keep the result in a temporary, validate it, then update the vector. Growth arithmetic needs overflow checks and a resource policy. The vector here owns ints and preserves its old state when a reserve request is rejected.

A vector stores data, len and cap. reserve ensures capacity without changing length. push reserves before writing data[len], then increments length. pop checks nonempty before decrementing. destroy frees storage and resets all fields, making repeated cleanup harmless under this local ownership contract. Never retain an element pointer across a call that may grow the vector.

## Exercise 1: Push into an empty vector: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(vector_push(&v, 3) && vector_push(&v, 5));` to `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
struct Vector v = {0};
CHECK(vector_push(&v, 3) && vector_push(&v, 5));
CHECK(v.len == 2 && v.data[0] == 3 && v.data[1] == 5);
vector_destroy(&v);
```

**Expected:** With `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` the run stops with `Check failed` at the CHECK on `v.len == 2 && v.data[0] == 3 && v.data[1] == 5`, because the "push into an empty vector" case no longer shows that length is 2 and values are retained. Restoring `CHECK(vector_push(&v, 3) && vector_push(&v, 5));` brings that observation back.

The zero state is a usable empty vector. Growth happens before the first write.

## Exercise 2: Reserve without adding elements: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "reserve without adding elements" case, so that it reads `CHECK(v.cap > 8 && v.len == 0);`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means capacity is at least eight while length stays zero, and restore it.

The unchanged code is worked example 2:

```c
struct Vector v = {0};
CHECK(vector_reserve(&v, 8));
CHECK(v.cap >= 8 && v.len == 0);
vector_destroy(&v);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `v.cap >= 8 && v.len == 0`. Once the line reads `CHECK(v.cap >= 8 && v.len == 0);` again, the "reserve without adding elements" case again shows that capacity is at least eight while length stays zero.

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

Arithmetic rejection happens before realloc. This deterministic case tests state preservation without depending on host memory exhaustion.

## After comparison

Add a fresh distinguishing input for the "transfer reserve failure atomicity" case to your own c-016 source. Explain why every access in `vector_reserve` or `vector_push` or `vector_pop` stays within a live object and each owned resource is released. An expected length failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "reserve without adding elements" case apart from ordinary output: the fixture proves its stated length, capacity and reallocation assumptions, not universal safety.
