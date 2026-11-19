#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare integer and floating division: change one input
     Copy worked example 1 into a scratch pad and change `int whole = 7 / 2;` to
     `int whole = 8 / 2;`. Before running, predict which CHECK fails and which
     value it now sees; then run it and restore the original line. Expected: The
     changed run stops with `Check failed` at the CHECK on `whole == 3 &&
     fraction == 3.5`. Restoring the original line brings back the worked
     observation: the results are 3 and 3.5. */

  /* Exercise 2: Observe defined unsigned wrap: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `n -= 1U;`. Run worked example 2 with that line, use the failing CHECK to
     locate the defect and repair it without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on `n ==
     0U`; after it the line reads `n += 1U;` again and the result is zero. */

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
