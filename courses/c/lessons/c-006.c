#include <stdio.h>

int main(void) {
  /* Exercise 1: Derive a local element count: predict an edited check
     In worked example 1, change `CHECK(n == 3);` to `CHECK(n == 4);`. Predict
     whether the CHECK still holds and why, then run and restore. Expected:
     `Check failed`: `CHECK(n == 4);` is false, although the count is 3. */

  /* Exercise 2: Pass an explicit length: debug a regression
     Worked example 2 now has a line reading `int values[] = {3, 4, 6};`. Repair
     it so that the result is 12 again. Expected: `Check failed` at
     `sum_items(values, 3) == 12` until the line reads `int values[] = {2, 4,
     6};` again. */

  /* Exercise 3: Inspect partial initialization
     Initialize only the first element of a three-element array.
     Expected: The remaining two elements are zero. */

  /* Exercise 4: Use a logical prefix
     Sum only the first two elements of a three-element array.
     Expected: The result is 6. */

  /* Exercise 5: Handle an empty logical view
     Call the sum contract with null and length zero.
     Expected: The sum is zero and no access occurs. */

  /* Exercise 6: Transfer independent array storage
     Copy elements into a distinct array and mutate the copy.
     Expected: The original first element remains 1. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
