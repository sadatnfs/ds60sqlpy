#include <stdio.h>

int main(void) {
  /* Exercise 1: Summarize valid records: change one input
     Copy worked example 1, the "summarize valid records" case, into a scratch
     pad and change `const char *rows[] = {"alpha,3", "beta,4"};` to `const char
     *rows[] = {"alpha,4", "beta,4"};`. Before running, predict which CHECK
     fails and which value it sees in place of the worked result (two rows
     produce total 7); then run it and restore the original line. Expected: With
     `const char *rows[] = {"alpha,4", "beta,4"};` the run stops with `Check
     failed` at the CHECK on `summarize(rows, 2, &out) && out.rows == 2 &&
     out.total == 7`, because the "summarize valid records" case no longer shows
     that two rows produce total 7. Restoring `const char *rows[] = {"alpha,3",
     "beta,4"};` brings that observation back. */

  /* Exercise 2: Reject a malformed record: debug a regression
     A regression changed one token in worked example 2, the "reject a malformed
     record" case, so one line now reads `struct Summary out = {10, 99};`. Run
     the example with that line, use the failing CHECK to find why the batch
     fails and the previous summary remains unchanged no longer holds and repair
     the line without changing the CHECK. Expected: Before the repair the run
     stops with `Check failed` at the CHECK on `!summarize(rows, 2, &out) &&
     out.rows == 9 && out.total == 99`. Once the line reads `struct Summary out
     = {9, 99};` again, the "reject a malformed record" case again shows that
     the batch fails and the previous summary remains unchanged. */

  /* Exercise 3: Handle an empty batch
     Summarize zero records.
     Expected: Rows and total are both zero. */

  /* Exercise 4: Reject extra field syntax
     Parse a line with two commas.
     Expected: The record is rejected. */

  /* Exercise 5: Preserve a legitimate zero
     Process alpha,0.
     Expected: One row contributes zero to the total. */

  /* Exercise 6: Transfer repeatable recovery
     Fail one batch, then run a corrected batch against the same output.
     Expected: Only the corrected complete batch publishes total 8. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
