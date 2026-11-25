# c-023: explained solutions

`c-023_solution.c` assembles the "insert and retrieve" case through the "transfer replacement while full" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A hash table maps a key to a candidate storage position. Different keys can collide, so a hash value is not proof of key equality. Open addressing resolves collisions by probing alternative slots under a bounded policy. Each slot needs occupancy information separate from its stored key and value, because zero may be a legitimate key or value. Deletion in an open-addressed table requires care: clearing a slot can break the search chain for later colliding entries. This small fixed table supports insertion, replacement and lookup, and deliberately does not pretend that naive clearing implements deletion.

The fixture uses unsigned integer keys and linear probing across eight slots. Every probe checks used and then compares the actual key. A probe loop has a capacity bound so a full table cannot cause an infinite search. Inserting an existing key replaces its value without consuming another slot. Production designs choose a load factor, resizing policy, hash function and collision-resistance requirements from their input threat model.

## Exercise 1: Insert and retrieve: predict an edited check

In worked example 1, change `CHECK(table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7);` to `CHECK(table_put(&t, 2, 7) && table_get(&t, 1, &out) && out == 7);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
struct Table t = {0};
int out = 0;
CHECK(table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7);
```

**Expected:** `Check failed`: `CHECK(table_put(&t, 2, 7) && table_get(&t, 1, &out) && out == 7);` is false, although lookup succeeds with 7.

**Verify:** Explain which claim `CHECK(table_put(&t, 2, 7) && table_get(&t, 1, &out) && out == 7);` makes that the state fails; restoring `CHECK(table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7);` passes again.

Lookup checks the actual key rather than trusting the initial slot alone.

## Exercise 2: Resolve a collision: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(table_put(&t, 1, 10) && table_put(&t, 10, 90));`. Explain why it fails although both values remain retrievable, then restore it.

The unchanged code is worked example 2:

```c
struct Table t = {0};
int out = 0;
CHECK(table_put(&t, 1, 10) && table_put(&t, 9, 90));
CHECK(table_get(&t, 1, &out) && out == 10);
CHECK(table_get(&t, 9, &out) && out == 90);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(table_put(&t, 1, 10) && table_put(&t, 9, 90));` again, though both values remain retrievable.

**Verify:** Explain why `CHECK(table_put(&t, 1, 10) && table_put(&t, 10, 90));` rejects a state that `table_get(&t, 9, &out) && out == 90` accepts, using your failing and repaired runs.

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

**Verify:** Keep a CHECK equivalent to `table_get(&t, 2, &out) && out == 8`. Control edit: `CHECK(table_put(&t, 2, 3) && table_put(&t, 3, 8));` must fail; then restore it.

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

**Verify:** Keep a CHECK equivalent to `!table_get(&t, 3, &out) && out == 9`. Control edit: changing `out = 9;` to `out = 10;` must fail it; then restore it.

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

**Verify:** Keep a CHECK equivalent to `!table_put(&t, 99, 99)`. Control edit: changing `for (unsigned i = 0; i < 8; i++)` to `for (unsigned i = 1; i < 8; i++)` must fail it; then restore it.

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

**Verify:** Keep a CHECK equivalent to `table_put(&t, 3, 30) && table_get(&t, 3, &out) && out == 30`. Control edit: `CHECK(table_put(&t, 4, 30) && table_get(&t, 3, &out) && out == 30);` must fail; then restore it.

Full storage prevents new keys, not an update to an already present key. This is a distinct edge condition.

## After comparison

Insert the keys 1, 9 and 17, which all hash to slot 1 in this eight-slot table, and CHECK that `table_get` finds 17 in slot 3. Then look up 25, which also hashes to slot 1 but was never inserted, and CHECK that it reports absent only after probing slots 1, 2 and 3 and reaching the empty slot 4. Explain why stopping at the first mismatched key would lose 9 and 17.
