#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare integer and floating division: change one input
     In worked example 1, change `int whole = 7 / 2;` to `int whole = 8 / 2;`.
     Predict which value the CHECK on `whole == 3 && fraction == 3.5` sees, then
     run and restore. Expected: `Check failed` at `whole == 3 && fraction
     == 3.5`; restoring `int whole = 7 / 2;` passes again. */

  /* Exercise 2: Observe defined unsigned wrap: debug a regression
     Worked example 2 now has a line reading `n -= 1U;`. Repair it so that the
     result is zero again. Expected: `Check failed` at `n == 0U` until the line
     reads `n += 1U;` again. */

  /* Exercise 3: Inspect representation facts
     Check sizeof(char) and minimum CHAR_BIT.
     Expected: A char occupies one char unit and has at least eight bits. */

  /* Exercise 4: Widen before multiplication
     Multiply two int64_t values of 50000.
     Expected: The product is 2500000000. */

  /* Exercise 5: Check a tiny floating calculation
     Add 0.1 and 0.2 and compare to 0.3.
     Expected: The absolute error is below 1e-15. */

  /* Exercise 6: Transfer negative division
     Divide -7 by 2 and inspect its remainder.
     Expected: The quotient is -3 and remainder -1. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
