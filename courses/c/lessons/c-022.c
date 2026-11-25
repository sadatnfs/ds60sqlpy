#include <stdio.h>

int main(void) {
  /* Exercise 1: Preserve FIFO order: predict an edited check
     In worked example 1, change `CHECK(enqueue(&q, 2) && enqueue(&q, 5));` to
     `CHECK(enqueue(&q, 2) && enqueue(&q, 6));`. Predict whether the CHECK still
     holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(enqueue(&q, 2) && enqueue(&q, 6));` is false, although the values
     arrive as 2 then 5. */

  /* Exercise 2: Reject an empty read: debug a regression
     Worked example 2 now has a line reading `int out = 10;`. Repair it so that
     the operation fails and output stays 9 again. Expected: `Check failed` at
     `!dequeue(&q, &out) && out == 9 && q.count == 0` until the line reads `int
     out = 9;` again. */

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
