#include <stdio.h>

int main(void) {
  /* Exercise 1: Sum one field in records: change one input
     Copy worked example 1 into a scratch pad and change `struct Point records[]
     = {{1, 10}, {2, 20}, {3, 30}};` to `struct Point records[] = {{2, 10}, {2,
     20}, {3, 30}};`. Before running, predict which CHECK fails and which value
     it now sees; then run it and restore the original line. Expected: The
     changed run stops with `Check failed` at the CHECK on `sum == 6`. Restoring
     the original line brings back the worked observation: the result is 6. */

  /* Exercise 2: Compute the same result by columns: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `sum -= x[i];`. Run worked example 2 with that line, use the failing CHECK
     to locate the defect and repair it without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on `sum ==
     6 && y[2] == 30`; after it the line reads `sum += x[i];` again and the
     result is also 6. */

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
