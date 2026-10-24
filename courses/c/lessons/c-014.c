#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a complete integer
     Parse 42 into an output integer.
     Expected: Success is true and output is 42. */

  /* Exercise 2: Reject trailing garbage
     Parse 42x with an existing output of 7.
     Expected: The call fails and output remains 7. */

  /* Exercise 3: Reject empty input
     Parse an empty string.
     Expected: No numeric value is accepted. */

  /* Exercise 4: Reject an oversized number
     Parse a very long positive integer.
     Expected: The operation rejects the range overflow. */

  /* Exercise 5: Retain a valid negative value
     Parse -7.
     Expected: The output is -7. */

  /* Exercise 6: Transfer the whitespace policy
     Compare leading whitespace with trailing whitespace.
     Expected: Leading whitespace is accepted; trailing whitespace is rejected.
   */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
