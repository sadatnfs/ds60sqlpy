# c-022: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A stack removes the most recently inserted value; a queue removes the earliest. The same array storage can support different behavioral contracts. A bounded ring buffer reuses positions by wrapping indices modulo capacity. Keep occupancy separate from index values so full and empty are not confused when head equals tail. Every enqueue must prove spare capacity before writing, and every dequeue must prove nonempty state before reading. Fixed capacity makes resource use predictable and overflow behavior explicit. A concurrent queue requires additional synchronization; the sequential ring here is not automatically safe to share across threads.

The queue stores head and count. The next insertion index is (head+count)%capacity, and removal advances head modulo capacity. count ranges from zero through capacity. Returning bool plus an output pointer preserves the distinction between an empty queue and a legitimate zero-valued item. Rejected operations leave both structure and output unchanged.

## Exercise 1: Preserve FIFO order

Enqueue 2 then 5 and dequeue twice.

```c
struct Queue q = {0};
int out = 0;
CHECK(enqueue(&q, 2) && enqueue(&q, 5));
CHECK(dequeue(&q, &out) && out == 2);
CHECK(dequeue(&q, &out) && out == 5);
```

**Expected:** The values arrive as 2 then 5.

The queue contract differs from a stack, which would return 5 first.

## Exercise 2: Reject an empty read

Dequeue from a new queue with output 9.

```c
struct Queue q = {0};
int out = 9;
CHECK(!dequeue(&q, &out) && out == 9 && q.count == 0);
```

**Expected:** The operation fails and output stays 9.

No element is read before the occupancy check. Zero cannot be used as an empty sentinel because zero may be a real item.

## Exercise 3: Reject a full write

Fill four slots and attempt a fifth insertion.

```c
struct Queue q = {0};
for (int i = 0; i < 4; i++)
  CHECK(enqueue(&q, i));
CHECK(!enqueue(&q, 99) && q.count == 4);
```

**Expected:** The fifth fails and occupancy stays four.

A bounded container must state whether full means reject, overwrite or block. This one rejects without data loss.

## Exercise 4: Wrap reused storage

Fill, remove two values, then add two more.

```c
struct Queue q = {0};
int out = 0;
for (int i = 0; i < 4; i++)
  CHECK(enqueue(&q, i));
CHECK(dequeue(&q, &out) && dequeue(&q, &out));
CHECK(enqueue(&q, 4) && enqueue(&q, 5));
for (int i = 2; i < 6; i++) {
  CHECK(dequeue(&q, &out) && out == i);
}
```

**Expected:** Remaining order is 2, 3, 4, 5.

Wrapped physical positions still implement one logical FIFO sequence.

## Exercise 5: Retain a real zero

Enqueue zero and then read it.

```c
struct Queue q = {0};
int out = 9;
CHECK(enqueue(&q, 0) && dequeue(&q, &out) && out == 0);
```

**Expected:** The read succeeds with output zero.

Status and payload are separate channels, so an ordinary zero does not look like failure.

## Exercise 6: Transfer stack contrast

Push 2 and 5 into a bounded stack and pop once.

```c
int stack[4];
size_t length = 0;
stack[length++] = 2;
stack[length++] = 5;
int out = stack[--length];
CHECK(out == 5 && length == 1);
```

**Expected:** The popped value is 5.

The pop index is the last occupied position. This direct fixture proves nonempty state before decrementing.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
