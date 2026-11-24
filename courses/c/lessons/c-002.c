#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare integer and floating division: change one input
     Copy worked example 1, the "compare integer and floating division" case,
     into a scratch pad and change `int whole = 7 / 2;` to `int whole = 8 / 2;`.
     Before running, predict which CHECK fails and which value it sees in place
     of the worked result (the results are 3 and 3.5); then run it and restore
     the original line. Expected: With `int whole = 8 / 2;` the run stops with
     `Check failed` at the CHECK on `whole == 3 && fraction == 3.5`, because the
     "compare integer and floating division" case no longer shows that the
     results are 3 and 3.5. Restoring `int whole = 7 / 2;` brings that
     observation back. */

  /* Exercise 2: Observe defined unsigned wrap: debug a regression
     A regression changed one token in worked example 2, the "observe defined
     unsigned wrap" case, so one line now reads `n -= 1U;`. Run the example with
     that line, use the failing CHECK to find why the result is zero no longer
     holds and repair the line without changing the CHECK. Expected: Before the
     repair the run stops with `Check failed` at the CHECK on `n == 0U`. Once
     the line reads `n += 1U;` again, the "observe defined unsigned wrap" case
     again shows that the result is zero. */

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
