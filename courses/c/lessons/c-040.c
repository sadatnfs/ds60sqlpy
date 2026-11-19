#include <stdio.h>

int main(void) {
  /* Exercise 1: Use caller-owned output: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);` to
     `CHECK(copy_api("hello!", out, sizeof out, &required) == API_OK);` inside
     its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: The changed run stops with `Check
     failed` at the CHECK on `required == 5 && strcmp(out, "hello") == 0`.
     Restoring the original line brings back the worked observation: the output
     is complete and required length is 5. */

  /* Exercise 2: Report insufficient capacity: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `char out[4] = "old!";`. Run worked example 2 with that line, use the
     failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `required == 5 && strcmp(out, "old") == 0`; after it the line
     reads `char out[4] = "old";` again and the status is too-small and required
     length is 5. */

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
