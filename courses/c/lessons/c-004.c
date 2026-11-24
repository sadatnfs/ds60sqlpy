#include <stdio.h>

int main(void) {
  /* Exercise 1: Trace a prefix sum: change one input
     Copy worked example 1, the "trace a prefix sum" case, into a scratch pad
     and change `int values[] = {2, 4, 6};` to `int values[] = {3, 4, 6};`.
     Before running, predict which CHECK fails and which value it sees in place
     of the worked result (the result is 12); then run it and restore the
     original line. Expected: With `int values[] = {3, 4, 6};` the run stops
     with `Check failed` at the CHECK on `sum == 12`, because the "trace a
     prefix sum" case no longer shows that the result is 12. Restoring `int
     values[] = {2, 4, 6};` brings that observation back. */

  /* Exercise 2: Handle zero iterations: debug a regression
     A regression changed one token in worked example 2, the "handle zero
     iterations" case, so one line now reads `for (size_t i = 0; i <= length;
     i++) {`. Run the example with that line, use the failing CHECK to find why
     the accumulator remains zero no longer holds and repair the line without
     changing the CHECK. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `sum == 0`. Once the line reads `for (size_t i = 0;
     i < length; i++) {` again, the "handle zero iterations" case again shows
     that the accumulator remains zero. */

  /* Exercise 3: Find the first match
     Search 3, 8, 8 and stop on the first 8.
     Expected: The index is 1. */

  /* Exercise 4: Include an exact threshold
     Classify score 60 with passing threshold 60.
     Expected: The boundary passes. */

  /* Exercise 5: Terminate a switch case
     Map code 2 to value 20 with explicit breaks.
     Expected: The result is 20. */

  /* Exercise 6: Transfer reverse traversal safely
     Visit indices 2, 1 and 0 using a positive-count loop.
     Expected: The reversed number is 321. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
