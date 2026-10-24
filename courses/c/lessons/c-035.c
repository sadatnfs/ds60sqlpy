#include <stdio.h>

int main(void) {
  /* Exercise 1: Install and restore a handler
     Install the lesson handler for SIGINT and restore the previous disposition.
     Expected: Both operations succeed. */

  /* Exercise 2: Record a raised notification
     Raise SIGINT while the lesson handler is installed.
     Expected: The signal flag becomes one. */

  /* Exercise 3: Keep work outside the handler
     Translate an already set flag into a normal-flow shutdown decision.
     Expected: The normal-flow decision becomes stop. */

  /* Exercise 4: Handle no notification
     Inspect a cleared signal flag.
     Expected: The shutdown decision remains false. */

  /* Exercise 5: Reset between independent operations
     Set then clear the flag in ordinary control flow.
     Expected: The next operation begins without a stale notification. */

  /* Exercise 6: Transfer a bounded shutdown model
     Stop admitting work after observing the signal flag while retaining
     active-work count. Expected: Admission stops and unfinished work remains
     visible. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
