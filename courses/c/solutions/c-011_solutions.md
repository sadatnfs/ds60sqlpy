# c-011: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Scope determines where a name is visible; lifetime determines when its object exists. They are related but different. An automatic local object usually lasts until its block ends. A static-storage object exists for the program duration even when its name is visible only inside one function. Allocated storage has a lifetime controlled by allocation and release, taught next. A pointer does not extend any of these lifetimes automatically. Returning an automatic local address is invalid after return, while returning a static object address can be valid but introduces shared mutable state and reentrancy concerns.

A block can shadow an outer variable with the same name. static inside a function preserves one object across calls and zero-initializes it before execution. A file-scope static declaration also restricts linkage to the translation unit. These are different uses of the same keyword. Keep automatic variables explicitly initialized before reading them. Do not use the value of a pointer after its target lifetime has ended.

## Exercise 1: Trace block shadowing

Declare an outer value 3 and a separate inner value 7.

```c
int value = 3;
{
  int value = 7;
  CHECK(value == 7);
}
CHECK(value == 3);
```

**Expected:** After the inner block, the outer remains 3.

The names are the same but designate distinct objects. Shadowing can be legal while still reducing readability.

## Exercise 2: Retain static state

Call a function with one static counter twice.

```c
CHECK(next_count() == 1);
CHECK(next_count() == 2);
```

**Expected:** It returns 1 and then 2.

The counter is initialized once and survives function returns. This shared state would require synchronization if called concurrently.

## Exercise 3: Return a static address

Get a pointer to a static read-only value.

```c
const int *p = static_value();
CHECK(*p == 7);
```

**Expected:** The target remains valid and equals 7.

The target lifetime spans the program. const restricts mutation through this pointer but does not make every static design automatically thread-safe.

## Exercise 4: Keep automatic state per call

Call a function with an initialized local counter twice.

```c
CHECK(local_count() == 1 && local_count() == 1);
```

**Expected:** Both calls return 1.

Each call creates a fresh automatic object. This differs from the retained static counter.

## Exercise 5: Separate visibility from lifetime

Retain a value copy obtained from an inner block.

```c
int copy = 0;
{
  int local = 9;
  copy = local;
}
CHECK(copy == 9);
```

**Expected:** The copied scalar remains 9 afterward.

The scalar copy has its own lifetime. Retaining &local instead would produce an invalid pointer after the block.

## Exercise 6: Transfer initialized aggregation

Initialize an accumulator before processing an empty range.

```c
int total = 0;
size_t count = 0;
for (size_t i = 0; i < count; i++)
  total += (int)i;
CHECK(total == 0);
```

**Expected:** The result is the defined zero identity.

Reading an uninitialized automatic accumulator would not be repaired by an empty loop. Initialization is part of the algorithm.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
