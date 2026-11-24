#include <stdio.h>

int main(void) {
  /* Exercise 1: Use caller-owned output: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);` to
     `CHECK(copy_api("hello!", out, sizeof out, &required) == API_OK);` inside
     its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: With `CHECK(copy_api("hello!", out,
     sizeof out, &required) == API_OK);` the run stops with `Check failed` at
     the CHECK on `required == 5 && strcmp(out, "hello") == 0`, because the "use
     caller-owned output" case no longer shows that the output is complete and
     required length is 5. Restoring `CHECK(copy_api("hello", out, sizeof out,
     &required) == API_OK);` brings that observation back. */

  /* Exercise 2: Report insufficient capacity: debug a regression
     A regression changed one token in worked example 2, the "report
     insufficient capacity" case, so one line now reads `char out[4] = "old!";`.
     Run the example with that line, use the failing CHECK to find why the
     status is too-small and required length is 5 no longer holds and repair the
     line without changing the CHECK. Expected: Before the repair the run stops
     with `Check failed` at the CHECK on `required == 5 && strcmp(out, "old") ==
     0`. Once the line reads `char out[4] = "old";` again, the "report
     insufficient capacity" case again shows that the status is too-small and
     required length is 5. */

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
