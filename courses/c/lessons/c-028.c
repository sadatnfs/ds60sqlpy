#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a declared API: change one input
     In worked example 1, change `int values[] = {2, 4, 6};` to `int values[] =
     {3, 4, 6};`. Predict which value the CHECK on `stats_sum(values, 3) == 12`
     sees, then run and restore. Expected: `Check failed` at `stats_sum(values,
     3) == 12`; restoring `int values[] = {2, 4, 6};` passes again. */

  /* Exercise 2: Use an empty API contract: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(stats_sum(NULL, 0) != 0);`.
     Explain why it fails although the result is zero, then restore it.
     Expected: `Check failed` until the CHECK reads `CHECK(stats_sum(NULL, 0) ==
     0);` again, though the result is zero. */

  /* Exercise 3: Compare two callers
     Call the same helper with two separate arrays.
     Expected: The results are 3 and 7. */

  /* Exercise 4: Retain caller data
     Sum an array and inspect its elements afterward.
     Expected: The input remains unchanged. */

  /* Exercise 5: Check a one-element boundary
     Sum one negative value.
     Expected: The result is -3. */

  /* Exercise 6: Transfer repeatable builds to repeatable behavior
     Call the pure helper twice on the same input.
     Expected: Both results equal 6. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
