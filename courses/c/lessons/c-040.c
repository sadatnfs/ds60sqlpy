#include <stdio.h>

int main(void) {
  /* Exercise 1: Use caller-owned output
     Copy hello into sufficient caller storage through a status API.
     Expected: The output is complete and required length is 5. */

  /* Exercise 2: Report insufficient capacity
     Request the same copy into four bytes.
     Expected: The status is too-small and required length is 5. */

  /* Exercise 3: Support a size query
     Call with no output buffer and capacity zero.
     Expected: The required payload length is still reported. */

  /* Exercise 4: Reject a missing required-output pointer
     Call without a place to report required length.
     Expected: The API returns invalid. */

  /* Exercise 5: Keep fixed-width values exact
     Pass a uint32_t value through an identity boundary.
     Expected: All 32 bits remain unchanged. */

  /* Exercise 6: Transfer an empty payload
     Copy an empty string into one byte.
     Expected: The API succeeds and stores a terminator. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
