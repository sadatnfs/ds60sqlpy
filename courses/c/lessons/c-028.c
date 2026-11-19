#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a declared API: change one input
     Copy worked example 1 into a scratch pad and change `int values[] = {2, 4,
     6};` to `int values[] = {3, 4, 6};`. Before running, predict which CHECK
     fails and which value it now sees; then run it and restore the original
     line. Expected: The changed run stops with `Check failed` at the CHECK on
     `stats_sum(values, 3) == 12`. Restoring the original line brings back the
     worked observation: summing 2, 4, 6 returns 12. */

  /* Exercise 2: Use an empty API contract: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(stats_sum(NULL, 0) != 0);`. Run worked example 2 with that line,
     explain why the edited CHECK now fails for the same program state, and
     restore it. Expected: Before the repair the run stops with `Check failed`
     at the CHECK on `stats_sum(NULL, 0) == 0`; after it the line reads
     `CHECK(stats_sum(NULL, 0) == 0);` again and the result is zero. */

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
