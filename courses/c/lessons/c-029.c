#include <stdio.h>

int main(void) {
  /* Exercise 1: Copy a representation safely: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(restored ==
     original);` to `CHECK(restored != original);` inside its CHECK. Before
     running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: The changed run stops with `Check failed` at the
     CHECK on `restored == original`. Restoring the original line brings back
     the worked observation: the restored value is 1.5. */

  /* Exercise 2: Inspect bytes without type punning: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `sum -= bytes[i];`. Run worked example 2 with that line, use the failing
     CHECK to locate the defect and repair it without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `sum == 7u`; after it the line reads `sum += bytes[i];` again and the
     bytes sum to 7 whatever the byte order. */

  /* Exercise 3: Handle overlapping moves
     Shift abc right by one within a buffer using memmove.
     Expected: The buffer prefix becomes aabc. */

  /* Exercise 4: Keep typed access in a real object
     Copy an int value into another int with memcpy.
     Expected: The target value becomes 9. */

  /* Exercise 5: Inspect an alignment requirement
     Read the alignment of int and max_align_t.
     Expected: Both requirements are positive. */

  /* Exercise 6: Transfer a bounded byte copy
     Copy a four-byte payload into an equally sized destination.
     Expected: All bytes match exactly. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
