#include <stdio.h>

int main(void) {
  /* Exercise 1: Invoke through a function pointer: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(transform(4) ==
     8);` to `CHECK(transform(5) == 8);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: The changed run stops with `Check failed` at the CHECK on
     `transform(4) == 8`. Restoring the original line brings back the worked
     observation: the result is 8. */

  /* Exercise 2: Sort integers safely: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int values[] = {4, 1, 2};`. Run worked example 2 with that line, use the
     failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `values[0] == 1 && values[1] == 2 && values[2] == 3`; after it the
     line reads `int values[] = {3, 1, 2};` again and the order becomes 1, 2, 3.
   */

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
