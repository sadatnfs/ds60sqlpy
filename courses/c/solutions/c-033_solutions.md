# c-033: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A flexible array member lets a struct end with a variable-sized trailing region. It must be the final member and does not contribute ordinary array elements to sizeof the base struct. Allocate enough storage for both the header and payload, with overflow checks before addition and multiplication. Keeping related data in one allocation can simplify ownership and improve locality, but every accessor must still respect the recorded payload length. Copying only sizeof the header does not clone the trailing payload. C struct assignment and generic serialization need special care for this layout.

struct Packet { size_t length; unsigned char data[]; } declares a flexible member. Allocate sizeof(struct Packet)+length bytes after proving length<=SIZE_MAX-sizeof(struct Packet). The member may have alignment-related placement details, so access it through the declared member rather than guessing an offset. One free releases the entire owned record. This fixture stores bytes, avoiding additional element-alignment arithmetic.

## Exercise 1: Create a trailing payload

Create a packet containing bytes 1, 2, 3.

```c
unsigned char data[] = {1, 2, 3};
struct Packet *p = packet_create(data, 3);
CHECK(p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3);
free(p);
```

**Expected:** Length and all three bytes are retained.

One owner releases header and payload together.

## Exercise 2: Create an empty packet

Create a packet with length zero.

```c
struct Packet *p = packet_create(NULL, 0);
CHECK(p != NULL && p->length == 0);
free(p);
```

**Expected:** The header exists and records zero length.

The helper avoids calling memcpy on absent payload pointers when no bytes are requested.

## Exercise 3: Reject total-size overflow

Request SIZE_MAX payload bytes.

```c
CHECK(packet_create(NULL, SIZE_MAX) == NULL);
```

**Expected:** The operation returns NULL before allocation.

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

Construction copies input bytes. A borrowed-view API would require a different lifetime contract.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
