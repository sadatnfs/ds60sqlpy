#include <stdio.h>

int main(void) {
  /* Exercise 1: Use caller-owned output: predict an edited check
     In worked example 1, change `CHECK(copy_api("hello", out, sizeof out,
     &required) == API_OK);` to `CHECK(copy_api("hello!", out, sizeof out,
     &required) == API_OK);`. Predict whether the CHECK still holds and why,
     then run and restore. Expected: `Check failed`: `CHECK(copy_api("hello!",
     out, sizeof out, &required) == API_OK);` is false, although the output is
     complete and required length is 5. */

  /* Exercise 2: Report insufficient capacity: debug a regression
     Worked example 2 now has a line reading `char out[4] = "old!";`. Repair it
     so that the status is too-small and required length is 5 again. Expected:
     `Check failed` at `required == 5 && strcmp(out, "old") == 0` until the line
     reads `char out[4] = "old";` again. */

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
