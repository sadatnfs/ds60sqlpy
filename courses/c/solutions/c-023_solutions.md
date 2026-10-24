# c-023: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A hash table maps a key to a candidate storage position. Different keys can collide, so a hash value is not proof of key equality. Open addressing resolves collisions by probing alternative slots under a bounded policy. Each slot needs occupancy information separate from its stored key and value, because zero may be a legitimate key or value. Deletion in an open-addressed table requires care: clearing a slot can break the search chain for later colliding entries. This small fixed table supports insertion, replacement and lookup, and deliberately does not pretend that naive clearing implements deletion.

The fixture uses unsigned integer keys and linear probing across eight slots. Every probe checks used and then compares the actual key. A probe loop has a capacity bound so a full table cannot cause an infinite search. Inserting an existing key replaces its value without consuming another slot. Production designs choose a load factor, resizing policy, hash function and collision-resistance requirements from their input threat model.

## Exercise 1: Insert and retrieve

Store key 1 with value 7.

```c
struct Table t = {0};
int out = 0;
CHECK(table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7);
```

**Expected:** Lookup succeeds with 7.

Lookup checks the actual key rather than trusting the initial slot alone.

## Exercise 2: Resolve a collision

Insert keys 1 and 9, which share the initial slot.

```c
struct Table t = {0};
int out = 0;
CHECK(table_put(&t, 1, 10) && table_put(&t, 9, 90));
CHECK(table_get(&t, 1, &out) && out == 10);
CHECK(table_get(&t, 9, &out) && out == 90);
```

**Expected:** Both values remain retrievable.

Linear probing finds another free slot while preserving the key distinction.

## Exercise 3: Replace an existing key

Write key 2 twice with different values.

```c
struct Table t = {0};
int out = 0;
CHECK(table_put(&t, 2, 3) && table_put(&t, 2, 8));
CHECK(table_get(&t, 2, &out) && out == 8);
```

**Expected:** The latest value is 8.

Replacement does not create duplicate logical keys.

## Exercise 4: Distinguish absent from zero

Store key zero with value zero and query a missing key.

```c
struct Table t = {0};
int out = 9;
CHECK(table_put(&t, 0, 0) && table_get(&t, 0, &out) && out == 0);
out = 9;
CHECK(!table_get(&t, 3, &out) && out == 9);
```

**Expected:** The stored zero succeeds; the missing key fails.

Occupancy and return status preserve information that a zero sentinel would lose.

## Exercise 5: Reject a full-table insertion

Fill all eight slots and insert a new ninth key.

```c
struct Table t = {0};
for (unsigned i = 0; i < 8; i++)
  CHECK(table_put(&t, i, (int)i));
CHECK(!table_put(&t, 99, 99));
```

**Expected:** The operation returns false without looping forever.

Every probe sequence is bounded by capacity. A resizing implementation would allocate before changing the old table.

## Exercise 6: Transfer replacement while full

Replace an existing key after filling the table.

```c
struct Table t = {0};
for (unsigned i = 0; i < 8; i++)
  CHECK(table_put(&t, i, (int)i));
int out = 0;
CHECK(table_put(&t, 3, 30) && table_get(&t, 3, &out) && out == 30);
```

**Expected:** Replacement still succeeds.

Full storage prevents new keys, not an update to an already present key. This is a distinct edge condition.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
