# c-033: explained solutions

`c-033_solution.c` assembles the "create a trailing payload" case through the "transfer source independence" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A flexible array member lets a struct end with a variable-sized trailing region. It must be the final member and does not contribute ordinary array elements to sizeof the base struct. Allocate enough storage for both the header and payload, with overflow checks before addition and multiplication. Keeping related data in one allocation can simplify ownership and improve locality, but every accessor must still respect the recorded payload length. Copying only sizeof the header does not clone the trailing payload. C struct assignment and generic serialization need special care for this layout.

struct Packet { size_t length; unsigned char data[]; } declares a flexible member. Allocate sizeof(struct Packet)+length bytes after proving length<=SIZE_MAX-sizeof(struct Packet). The member may have alignment-related placement details, so access it through the declared member rather than guessing an offset. One free releases the entire owned record. This fixture stores bytes, avoiding additional element-alignment arithmetic.

## Exercise 1: Create a trailing payload: change one input

In worked example 1, change `unsigned char data[] = {1, 2, 3};` to `unsigned char data[] = {2, 2, 3};`. Predict which value the CHECK on `p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3` sees, then run and restore.

The unchanged code is worked example 1:

```c
unsigned char data[] = {1, 2, 3};
struct Packet *p = packet_create(data, 3);
CHECK(p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3);
free(p);
```

**Expected:** `Check failed` at `p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3`; restoring `unsigned char data[] = {1, 2, 3};` passes again.

**Verify:** Name the value that made `p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3` false, where worked example 1 showed that length and all three bytes are retained.

One owner releases header and payload together.

## Exercise 2: Create an empty packet: debug a regression

Worked example 2 now has a line reading `struct Packet *p = packet_create(NULL, 1);`. Repair it so that the header exists and records zero length again.

The unchanged code is worked example 2:

```c
struct Packet *p = packet_create(NULL, 0);
CHECK(p != NULL && p->length == 0);
free(p);
```

**Expected:** `Check failed` at `p != NULL && p->length == 0` until the line reads `struct Packet *p = packet_create(NULL, 0);` again.

**Verify:** Explain how `struct Packet *p = packet_create(NULL, 1);` changes the value `p != NULL && p->length == 0` tests, using your failing and repaired runs.

The helper avoids calling memcpy on absent payload pointers when no bytes are requested.

## Exercise 3: Reject total-size overflow

Request SIZE_MAX payload bytes.

```c
CHECK(packet_create(NULL, SIZE_MAX) == NULL);
```

**Expected:** The operation returns NULL before allocation.

**Verify:** Keep a CHECK equivalent to `packet_create(NULL, SIZE_MAX) == NULL`. Control edit: `CHECK(packet_create(NULL, SIZE_MAX) != NULL);` must fail; then restore it.

Checking the addition before allocation prevents a wrapped header-plus-payload size.

## Exercise 4: Clone the complete record

Create two packets from the same source and mutate one.

```c
unsigned char data[] = {4, 5};
struct Packet *a = packet_create(data, 2), *b = packet_create(data, 2);
CHECK(a != NULL && b != NULL);
b->data[0] = 9;
CHECK(a->data[0] == 4 && b->data[0] == 9);
free(a);
free(b);
```

**Expected:** The other payload remains unchanged.

**Verify:** Keep a CHECK equivalent to `a->data[0] == 4 && b->data[0] == 9`. Control edit: changing `unsigned char data[] = {4, 5};` to `unsigned char data[] = {5, 5};` must fail it; then restore it.

Separate complete allocations create independent owners. A base-struct assignment would not copy the flexible payload.

## Exercise 5: Preserve binary zero

Store a payload containing a zero byte.

```c
unsigned char data[] = {7, 0, 8};
struct Packet *p = packet_create(data, 3);
CHECK(p != NULL && p->length == 3 && p->data[1] == 0);
free(p);
```

**Expected:** Length remains three and the zero is retained.

**Verify:** Keep a CHECK equivalent to `p != NULL && p->length == 3 && p->data[1] == 0`. Control edit: changing `unsigned char data[] = {7, 0, 8};` to `unsigned char data[] = {7, 1, 8};` must fail it; then restore it.

The payload is length-delimited binary data rather than a C string.

## Exercise 6: Transfer source independence

Change the original source after packet construction.

```c
unsigned char data[] = {1};
struct Packet *p = packet_create(data, 1);
CHECK(p != NULL);
data[0] = 9;
CHECK(p->data[0] == 1);
free(p);
```

**Expected:** The owned packet retains its copied value.

**Verify:** Keep a CHECK equivalent to `p->data[0] == 1`. Control edit: changing `unsigned char data[] = {1};` to `unsigned char data[] = {2};` must fail it; then restore it.

Construction copies input bytes. A borrowed-view API would require a different lifetime contract.

## After comparison

Create a packet from a four-byte payload and CHECK that `p->data[3]` holds the last byte. Then CHECK `offsetof(struct Packet, data) <= sizeof(struct Packet)` and explain why `sizeof *p + length` is therefore enough even if padding follows `length`. Finally explain why declaring `unsigned char data[1]` instead would make the size arithmetic disagree with the record's real layout.
