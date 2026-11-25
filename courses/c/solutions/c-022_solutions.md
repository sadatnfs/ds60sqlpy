# c-022: explained solutions

`c-022_solution.c` assembles the "preserve FIFO order" case through the "transfer stack contrast" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A stack removes the most recently inserted value; a queue removes the earliest. The same array storage can support different behavioral contracts. A bounded ring buffer reuses positions by wrapping indices modulo capacity. Keep occupancy separate from index values so full and empty are not confused when head equals tail. Every enqueue must prove spare capacity before writing, and every dequeue must prove nonempty state before reading. Fixed capacity makes resource use predictable and overflow behavior explicit. A concurrent queue requires additional synchronization; the sequential ring here is not automatically safe to share across threads.

The queue stores head and count. The next insertion index is (head+count)%capacity, and removal advances head modulo capacity. count ranges from zero through capacity. Returning bool plus an output pointer preserves the distinction between an empty queue and a legitimate zero-valued item. Rejected operations leave both structure and output unchanged.

## Exercise 1: Preserve FIFO order: predict an edited check

In worked example 1, change `CHECK(enqueue(&q, 2) && enqueue(&q, 5));` to `CHECK(enqueue(&q, 2) && enqueue(&q, 6));`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
struct Queue q = {0};
int out = 0;
CHECK(enqueue(&q, 2) && enqueue(&q, 5));
CHECK(dequeue(&q, &out) && out == 2);
CHECK(dequeue(&q, &out) && out == 5);
```

**Expected:** `Check failed`: `CHECK(enqueue(&q, 2) && enqueue(&q, 6));` is false, although the values arrive as 2 then 5.

The queue contract differs from a stack, which would return 5 first.

**Approach.** Trace the queue state through the edited insertion: `enqueue(&q, 6)` stores 6 at index `(head + count) % 4`, which is 1, so the queue holds 2 and then 6.

**Why it holds here.** FIFO removal returns values in insertion order. The first `dequeue` still yields 2 and passes, but the second yields 6, so `out == 5` is false and the run stops at that third CHECK, not at the edited one.

**A plausible wrong approach.** Predicting that the edited CHECK itself fails because the stored value changed. `enqueue` returns true whenever there is spare capacity, and the queue is empty, so the edited line passes; only the later comparison with 5 sees the different value.

**Verify.** Run the edited pad and see `Check failed` reported on the line with `out == 5`; restore 5 and see `Worked example checks passed.`

## Exercise 2: Reject an empty read: debug a regression

Worked example 2 now has a line reading `int out = 10;`. Repair it so that the operation fails and output stays 9 again.

The unchanged code is worked example 2:

```c
struct Queue q = {0};
int out = 9;
CHECK(!dequeue(&q, &out) && out == 9 && q.count == 0);
```

**Expected:** `Check failed` at `!dequeue(&q, &out) && out == 9 && q.count == 0` until the line reads `int out = 9;` again.

No element is read before the occupancy check. Zero cannot be used as an empty sentinel because zero may be a real item.

**Approach.** Read the empty-queue contract: `dequeue` on `count == 0` returns false and must not write `*out`, so `out` keeps its initial value.

**Why it holds here.** With `int out = 10;` the rejected read leaves 10 in `out`, so `out == 9` is false even though `!dequeue(&q, &out)` and `q.count == 0` both hold. Restoring the initializer 9 repairs the run without touching the helper.

**A plausible wrong approach.** Changing `dequeue` to store a sentinel such as 0 or 9 on failure so the CHECK passes. That hides a real item of the same value and breaks the rule that a rejected operation leaves its output unchanged.

**Verify.** Print `out` and `q.count` after the failed call and see `10 0` with the regression and `9 0` after the repair.

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

**Approach.** Fill all four slots, then call `enqueue(&q, 99)` and check that it returns false with `count` still 4.

**Why it holds here.** `enqueue` tests `q->count == QUEUE_CAPACITY` (4) before computing the write index, so the fifth call rejects without writing `q->data[(q->head + q->count) % QUEUE_CAPACITY]`, which would overwrite the oldest value 0.

**A plausible wrong approach.** Testing `head == tail` with a separate tail index to detect full. When the ring is full the tail wraps back to `head`, the same state as empty, so the queue cannot tell the two apart; storing `count` avoids that ambiguity.

**Verify.** After the rejected write, dequeue four times and see 0, 1, 2 and 3, proving nothing was overwritten.

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

**Approach.** Fill the ring, dequeue twice so `head` is 2, then enqueue 4 and 5, which land at physical indices 0 and 1 because `(2 + 2) % 4` is 0.

**Why it holds here.** Logical order follows `head` and `count`, not physical index, so the four dequeues read indices 2, 3, 0 and 1 and yield 2, 3, 4 and 5.

**A plausible wrong approach.** Writing new values at `head + count` without the modulo. With `head` 2 and `count` 2 the index 4 is one past the end of `data`, an out-of-bounds write that the sanitizer reports and that a plain run may silently survive.

**Verify.** Print `q.head` and the physical index of each write and see indices 0 and 1 for values 4 and 5.

## Exercise 5: Retain a real zero

Enqueue zero and then read it.

```c
struct Queue q = {0};
int out = 9;
CHECK(enqueue(&q, 0) && dequeue(&q, &out) && out == 0);
```

**Expected:** The read succeeds with output zero.

Status and payload are separate channels, so an ordinary zero does not look like failure.

**Approach.** Enqueue 0, dequeue it into `out` initialized to 9, and check both the returned status and the value 0.

**Why it holds here.** The `bool` return reports success separately from the payload written through `out`, so a legitimate 0 replaces 9 and the status is still true.

**A plausible wrong approach.** Making `dequeue` return the item and using 0 to mean empty. This queue can hold 0, so the caller could not distinguish an empty read from a stored zero.

**Verify.** Change the enqueued value to -1 and to 0 in turn; both reads succeed and store exactly the enqueued value.

## Exercise 6: Transfer stack contrast

Push 2 and 5 into a bounded stack and pop once.

```c
int stack[4];
size_t length = 0;
stack[length++] = 2;
stack[length++] = 5;
CHECK(length > 0);
int out = stack[--length];
CHECK(out == 5 && length == 1);
```

**Expected:** The popped value is 5.

The pop index is the last occupied position. `CHECK(length > 0)` proves the stack is nonempty before the decrement, so `stack[--length]` never wraps the unsigned `length` to `SIZE_MAX` and reads outside `stack`; a general pop must make the same test and report failure instead.

**Approach.** Push 2 and 5 by writing `stack[length++]`, check `length > 0`, then pop with `stack[--length]`.

**Why it holds here.** A stack removes the newest value: after two pushes `length` is 2, so the pop reads index 1 and yields 5, leaving `length` 1. The nonempty check runs before the decrement, so the unsigned `length` cannot wrap.

**A plausible wrong approach.** Popping with `stack[length--]`. The postfix form reads index 2, one past the last occupied slot, which holds an indeterminate value, so the pop returns garbage rather than 5.

**Verify.** Pop a second time and see 2 with `length` 0; a third pop must fail at `CHECK(length > 0)` instead of reading `stack[SIZE_MAX]`.

## After comparison

Write `bool push(int *stack, size_t cap, size_t *length, int value)` and `bool pop(int *stack, size_t *length, int *out)` that reject a full push and an empty pop without writing. Check that capacity 2 accepts 2 and 5, rejects 9, pops 5 then 2, and rejects a third pop with `*out` unchanged. Explain why the queue needs `count` to separate full from empty while the stack can use `length` alone.
