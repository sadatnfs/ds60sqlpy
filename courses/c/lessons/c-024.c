#include <stdio.h>

int main(void) {
  /* Exercise 1: Find an interior boundary: change one input
     In worked example 1, change `int values[] = {2, 4, 6, 8};` to `int values[]
     = {2, 5, 6, 8};`. Predict which value the CHECK on `lower_bound(values, 4,
     5) == 2` sees, then run and restore. Expected: `Check failed` at
     `lower_bound(values, 4, 5) == 2`; restoring `int values[] = {2, 4, 6, 8};`
     passes again. */

  /* Exercise 2: Find the first duplicate: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(lower_bound(values, 4, 4) ==
     1);`. Explain why it fails although the index is the first 3 at position 1,
     then restore it. Expected: `Check failed` until the CHECK reads
     `CHECK(lower_bound(values, 4, 3) == 1);` again, though the index is the
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
