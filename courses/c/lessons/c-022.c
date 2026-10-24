#include <stdio.h>

int main(void) {
  /* Exercise 1: Preserve FIFO order
     Enqueue 2 then 5 and dequeue twice.
     Expected: The values arrive as 2 then 5. */

  /* Exercise 2: Reject an empty read
     Dequeue from a new queue with output 9.
     Expected: The operation fails and output stays 9. */

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
