#include <stdio.h>

int main(void) {
  /* Exercise 1: Check a first value: change one input
     In worked example 1, change `int total = 2 + 3;` to `int total = 3 + 3;`.
     Predict which value the CHECK on `total == 5` sees, then run and restore.
     Expected: `Check failed` at `total == 5`; restoring `int total = 2 + 3;`
     passes again. */

  /* Exercise 2: Format a checked result: debug a regression
     Worked example 2 now has a line reading `int n = snprintf(out, sizeof out,
     "total=%d", 6);`. Repair it so that the result length is 7 and text is
     total=5 again. Expected: `Check failed` at `strcmp(out, "total=5") == 0`
     until the line reads `int n = snprintf(out, sizeof out, "total=%d", 5);`
     again. */

  /* Exercise 3: Trace statement order
     Start at 1, increment, then multiply by 3.
     Expected: The result is 6. */

  /* Exercise 4: Inspect a boolean condition
     Compare 4 with 4 and 4 with 5.
     Expected: Equality is true and inequality is true. */

  /* Exercise 5: Use an explicit return contract
     Call a helper returning the value 7.
     Expected: The caller receives 7. */

  /* Exercise 6: Transfer a receipt calculation
     Multiply 4 items by a unit amount of 6.
     Expected: The checked amount is 24. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
