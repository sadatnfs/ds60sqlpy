#include <stdio.h>

int main(void) {
  /* Exercise 1: Add ordinary values
     Add 7 and 5 through the checked helper.
     Expected: The result is 12. */

  /* Exercise 2: Reject positive overflow
     Add one to INT_MAX.
     Expected: The operation fails and preserves output. */

  /* Exercise 3: Reject negative overflow
     Add negative one to INT_MIN.
     Expected: The operation fails without evaluating the overflow. */

  /* Exercise 4: Accept exact boundaries
     Add zero to both int extremes.
     Expected: Both exact boundary values are accepted. */

  /* Exercise 5: Reject a size product
     Multiply SIZE_MAX by two through a size helper.
     Expected: The helper rejects it and preserves output. */

  /* Exercise 6: Transfer the zero product
     Multiply SIZE_MAX by zero.
     Expected: The checked mathematical result is zero. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
