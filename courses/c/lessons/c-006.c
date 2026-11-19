#include <stdio.h>

int main(void) {
  /* Exercise 1: Derive a local element count: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(n == 3);` to
     `CHECK(n == 4);` inside its CHECK. Before running, predict whether the
     CHECK still holds and explain why; then restore it. Expected: The changed
     run stops with `Check failed` at the CHECK on `n == 3`. Restoring the
     original line brings back the worked observation: the count is 3. */

  /* Exercise 2: Pass an explicit length: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int values[] = {3, 4, 6};`. Run worked example 2 with that line, use the
     failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `sum_items(values, 3) == 12`; after it the line reads `int
     values[] = {2, 4, 6};` again and the result is 12. */

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
