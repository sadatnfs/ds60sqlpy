#include <stdio.h>

int main(void) {
  /* Exercise 1: Summarize valid records: change one input
     Copy worked example 1 into a scratch pad and change `const char *rows[] =
     {"alpha,3", "beta,4"};` to `const char *rows[] = {"alpha,4", "beta,4"};`.
     Before running, predict which CHECK fails and which value it now sees; then
     run it and restore the original line. Expected: The changed run stops with
     `Check failed` at the CHECK on `summarize(rows, 2, &out) && out.rows == 2
     && out.total == 7`. Restoring the original line brings back the worked
     observation: two rows produce total 7. */

  /* Exercise 2: Reject a malformed record: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `struct Summary out = {10, 99};`. Run worked example 2 with that line, use
     the failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99`;
     after it the line reads `struct Summary out = {9, 99};` again and the batch
     fails and the previous summary remains unchanged. */

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
