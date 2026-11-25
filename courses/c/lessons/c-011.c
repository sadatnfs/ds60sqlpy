#include <stdio.h>

int main(void) {
  /* Exercise 1: Trace block shadowing: change one input
     In worked example 1, change `int value = 3;` to `int value = 4;`. Predict
     which value the CHECK on `value == 3` sees, then run and restore. Expected:
     `Check failed` at `value == 3`; restoring `int value = 3;` passes again. */

  /* Exercise 2: Retain static state: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(next_count() != 2);`. Explain why
     it fails although it returns 1 and then 2, then restore it. Expected:
     `Check failed` until the CHECK reads `CHECK(next_count() == 2);` again,
     though it returns 1 and then 2. */

  /* Exercise 3: Return a static address
     Get a pointer to a static read-only value.
     Expected: The target remains valid and equals 7. */

  /* Exercise 4: Keep automatic state per call
     Call a function with an initialized local counter twice.
     Expected: Both calls return 1. */

  /* Exercise 5: Separate visibility from lifetime
     Retain a value copy obtained from an inner block.
     Expected: The copied scalar remains 9 afterward. */

  /* Exercise 6: Transfer initialized aggregation
     Initialize an accumulator before processing an empty range.
     Expected: The result is the defined zero identity. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
