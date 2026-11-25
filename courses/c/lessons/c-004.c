#include <stdio.h>

int main(void) {
  /* Exercise 1: Trace a prefix sum: change one input
     In worked example 1, change `int values[] = {2, 4, 6};` to `int values[] =
     {3, 4, 6};`. Predict which value the CHECK on `sum == 12` sees, then run
     and restore. Expected: `Check failed` at `sum == 12`; restoring `int
     values[] = {2, 4, 6};` passes again. */

  /* Exercise 2: Handle zero iterations: debug a regression
     Worked example 2 now has a line reading `for (size_t i = 0; i <= length;
     i++) {`. Repair it so that the accumulator remains zero again. Expected:
     `Check failed` at `sum == 0` until the line reads `for (size_t i = 0; i <
     length; i++) {` again. */

  /* Exercise 3: Find the first match
     Search 3, 8, 8 and stop on the first 8.
     Expected: The index is 1. */

  /* Exercise 4: Include an exact threshold
     Classify score 60 with passing threshold 60.
     Expected: The boundary passes. */

  /* Exercise 5: Terminate a switch case
     Map code 2 to value 20 with explicit breaks.
     Expected: The result is 20. */

  /* Exercise 6: Transfer reverse traversal safely
     Visit indices 2, 1 and 0 using a positive-count loop.
     Expected: The reversed number is 321. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
