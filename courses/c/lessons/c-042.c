#include <stdio.h>

int main(void) {
  /* Exercise 1: Summarize valid records: change one input
     In worked example 1, change `const char *rows[] = {"alpha,3", "beta,4"};`
     to `const char *rows[] = {"alpha,4", "beta,4"};`. Predict which value the
     CHECK on `summarize(rows, 2, &out) && out.rows == 2 && out.total == 7`
     sees, then run and restore. Expected: `Check failed` at `summarize(rows, 2,
     &out) && out.rows == 2 && out.total == 7`; restoring `const char *rows[] =
     {"alpha,3", "beta,4"};` passes again. */

  /* Exercise 2: Reject a malformed record: debug a regression
     Worked example 2 now has a line reading `struct Summary out = {10, 99};`.
     Repair it so that the batch fails and the previous summary remains
     unchanged again. Expected: `Check failed` at `!summarize(rows, 2, &out) &&
     out.rows == 9 && out.total == 99` until the line reads `struct Summary out
     = {9, 99};` again. */

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
