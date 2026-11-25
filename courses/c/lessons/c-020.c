#include <stdio.h>

int main(void) {
  /* Exercise 1: Invoke through a function pointer: predict an edited check
     In worked example 1, change `CHECK(transform(4) == 8);` to
     `CHECK(transform(5) == 8);`. Predict whether the CHECK still holds and why,
     then run and restore. Expected: `Check failed`: `CHECK(transform(5) == 8);`
     is false, although the result is 8. */

  /* Exercise 2: Sort integers safely: debug a regression
     Worked example 2 now has a line reading `int values[] = {4, 1, 2};`. Repair
     it so that the order becomes 1, 2, 3 again. Expected: `Check failed` at
     `values[0] == 1 && values[1] == 2 && values[2] == 3` until the line reads
     `int values[] = {3, 1, 2};` again. */

  /* Exercise 3: Compare extreme values
     Compare INT_MIN and INT_MAX.
     Expected: The result correctly reports the first is smaller. */

  /* Exercise 4: Retain equal values
     Sort duplicate values 2, 1, 2.
     Expected: Both copies of 2 remain. */

  /* Exercise 5: Inject a predicate
     Count even values in 1, 2, 3, 4 through a callback.
     Expected: The count is 2. */

  /* Exercise 6: Transfer an empty callback traversal
     Count over zero logical elements.
     Expected: The result is zero and no element is accessed. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
