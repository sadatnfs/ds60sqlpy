#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a declared API: change one input
     Copy worked example 1, the "call a declared API" case, into a scratch pad
     and change `int values[] = {2, 4, 6};` to `int values[] = {3, 4, 6};`.
     Before running, predict which CHECK fails and which value it sees in place
     of the worked result (summing 2, 4, 6 returns 12); then run it and restore
     the original line. Expected: With `int values[] = {3, 4, 6};` the run stops
     with `Check failed` at the CHECK on `stats_sum(values, 3) == 12`, because
     the "call a declared API" case no longer shows that summing 2, 4, 6
     returns 12. Restoring `int values[] = {2, 4, 6};` brings that observation
     back. */

  /* Exercise 2: Use an empty API contract: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "use an empty
     API contract" case, so that it reads `CHECK(stats_sum(NULL, 0) != 0);`. Run
     the example with that line, explain why the edited CHECK now fails even
     though the program state still means the result is zero, and restore it.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `stats_sum(NULL, 0) == 0`. Once the line reads `CHECK(stats_sum(NULL, 0)
     == 0);` again, the "use an empty API contract" case again shows that the
     result is zero. */

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
