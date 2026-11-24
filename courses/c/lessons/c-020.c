#include <stdio.h>

int main(void) {
  /* Exercise 1: Invoke through a function pointer: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(transform(4) ==
     8);` to `CHECK(transform(5) == 8);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: With `CHECK(transform(5) == 8);` the run stops with `Check
     failed` at the CHECK on `transform(4) == 8`, because the "invoke through a
     function pointer" case no longer shows that the result is 8. Restoring
     `CHECK(transform(4) == 8);` brings that observation back. */

  /* Exercise 2: Sort integers safely: debug a regression
     A regression changed one token in worked example 2, the "sort integers
     safely" case, so one line now reads `int values[] = {4, 1, 2};`. Run the
     example with that line, use the failing CHECK to find why the order becomes
     1, 2, 3 no longer holds and repair the line without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `values[0] == 1 && values[1] == 2 && values[2] == 3`. Once the line
     reads `int values[] = {3, 1, 2};` again, the "sort integers safely" case
     again shows that the order becomes 1, 2, 3. */

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
