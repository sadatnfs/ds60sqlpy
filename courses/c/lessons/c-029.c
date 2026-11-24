#include <stdio.h>

int main(void) {
  /* Exercise 1: Copy a representation safely: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(restored ==
     original);` to `CHECK(restored != original);` inside its CHECK. Before
     running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: With `CHECK(restored != original);` the run stops
     with `Check failed` at the CHECK on `restored == original`, because the
     "copy a representation safely" case no longer shows that the restored value
     is 1.5. Restoring `CHECK(restored == original);` brings that observation
     back. */

  /* Exercise 2: Inspect bytes without type punning: debug a regression
     A regression changed one token in worked example 2, the "inspect bytes
     without type punning" case, so one line now reads `sum -= bytes[i];`. Run
     the example with that line, use the failing CHECK to find why the bytes sum
     to 7 whatever the byte order no longer holds and repair the line without
     changing the CHECK. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `sum == 7u`. Once the line reads `sum += bytes[i];`
     again, the "inspect bytes without type punning" case again shows that the
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
