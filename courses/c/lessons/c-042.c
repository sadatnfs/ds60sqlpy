#include <stdio.h>

int main(void) {
  /* Exercise 1: Summarize valid records
     Process alpha,3 and beta,4.
     Expected: Two rows produce total 7. */

  /* Exercise 2: Reject a malformed record
     Process one valid record followed by a negative count.
     Expected: The batch fails and the previous summary remains unchanged. */

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
