#include <stdio.h>

int main(void) {
  /* Exercise 1: Preserve FIFO order: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(enqueue(&q, 2)
     && enqueue(&q, 5));` to `CHECK(enqueue(&q, 2) && enqueue(&q, 6));` inside
     its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: The changed run stops with `Check
     failed` at the CHECK on `dequeue(&q, &out) && out == 5`. Restoring the
     original line brings back the worked observation: the values arrive as 2
     then 5. */

  /* Exercise 2: Reject an empty read: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int out = 10;`. Run worked example 2 with that line, use the failing CHECK
     to locate the defect and repair it without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `!dequeue(&q, &out) && out == 9 && q.count == 0`; after it the line reads
     `int out = 9;` again and the operation fails and output stays 9. */

  /* Exercise 3: Reject a full write
     Fill four slots and attempt a fifth insertion.
     Expected: The fifth fails and occupancy stays four. */

  /* Exercise 4: Wrap reused storage
     Fill, remove two values, then add two more.
     Expected: Remaining order is 2, 3, 4, 5. */

  /* Exercise 5: Retain a real zero
     Enqueue zero and then read it.
     Expected: The read succeeds with output zero. */

  /* Exercise 6: Transfer stack contrast
     Push 2 and 5 into a bounded stack and pop once.
     Expected: The popped value is 5. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
