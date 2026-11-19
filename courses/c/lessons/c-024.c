#include <stdio.h>

int main(void) {
  /* Exercise 1: Find an interior boundary: change one input
     Copy worked example 1 into a scratch pad and change `int values[] = {2, 4,
     6, 8};` to `int values[] = {2, 5, 6, 8};`. Before running, predict which
     CHECK fails and which value it now sees; then run it and restore the
     original line. Expected: The changed run stops with `Check failed` at the
     CHECK on `lower_bound(values, 4, 5) == 2`. Restoring the original line
     brings back the worked observation: the lower-bound index is 2. */

  /* Exercise 2: Find the first duplicate: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(lower_bound(values, 4, 4) == 1);`. Run worked example 2 with that
     line, explain why the edited CHECK now fails for the same program state,
     and restore it. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `lower_bound(values, 4, 3) == 1`; after it the line
     reads `CHECK(lower_bound(values, 4, 3) == 1);` again and the index is the
     first 3 at position 1. */

  /* Exercise 3: Handle no larger value
     Search 2, 4, 6 for target 9.
     Expected: The result is length 3. */

  /* Exercise 4: Handle empty input
     Search an empty logical view.
     Expected: The insertion index is zero. */

  /* Exercise 5: Check the first boundary
     Search 2, 4, 6 for target 1.
     Expected: The index is zero. */

  /* Exercise 6: Transfer an exact membership check
     Use lower bound and then equality to test whether 4 is present.
     Expected: The guarded membership test succeeds. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
