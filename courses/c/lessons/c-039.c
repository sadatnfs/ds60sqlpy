#include <stdio.h>

int main(void) {
  /* Exercise 1: Sum one field in records: change one input
     In worked example 1, change `struct Point records[] = {{1, 10}, {2, 20},
     {3, 30}};` to `struct Point records[] = {{2, 10}, {2, 20}, {3, 30}};`.
     Predict which value the CHECK on `sum == 6` sees, then run and restore.
     Expected: `Check failed` at `sum == 6`; restoring `struct Point records[] =
     {{1, 10}, {2, 20}, {3, 30}};` passes again. */

  /* Exercise 2: Compute the same result by columns: debug a regression
     Worked example 2 now has a line reading `sum -= x[i];`. Repair it so that
     the result is also 6 again. Expected: `Check failed` at `sum == 6 && y[2]
     == 30` until the line reads `sum += x[i];` again. */

  /* Exercise 3: Inspect legal field offsets
     Inspect x and y offsets in Point.
     Expected: Offsets are within the struct and preserve declaration order. */

  /* Exercise 4: Count algorithmic work
     Scan six values and count iterations.
     Expected: Exactly six visits occur. */

  /* Exercise 5: Preserve result under blocking
     Sum the same data in blocks of two.
     Expected: The total remains 21. */

  /* Exercise 6: Transfer a partial block
     Sum five values in blocks of two with a bounded final block.
     Expected: The total is 15 without a sixth access. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
