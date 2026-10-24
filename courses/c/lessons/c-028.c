#include <stdio.h>

int main(void) {
  /* Exercise 1: Call a declared API
     Use the stats_sum prototype before its definition.
     Expected: Summing 2, 4, 6 returns 12. */

  /* Exercise 2: Use an empty API contract
     Sum a zero-length view.
     Expected: The result is zero. */

  /* Exercise 3: Compare two callers
     Call the same helper with two separate arrays.
     Expected: The results are 3 and 7. */

  /* Exercise 4: Retain caller data
     Sum an array and inspect its elements afterward.
     Expected: The input remains unchanged. */

  /* Exercise 5: Check a one-element boundary
     Sum one negative value.
     Expected: The result is -3. */

  /* Exercise 6: Transfer repeatable builds to repeatable behavior
     Call the pure helper twice on the same input.
     Expected: Both results equal 6. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
