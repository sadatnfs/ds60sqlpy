#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare integer and floating division
     Compute 7/2 and 7/2.0.
     Expected: The results are 3 and 3.5. */

  /* Exercise 2: Observe defined unsigned wrap
     Add one to UINT_MAX in unsigned arithmetic.
     Expected: The result is zero. */

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
