#include <stdio.h>

int main(void) {
  /* Exercise 1: Copy a representation safely: predict an edited check
     In worked example 1, change `CHECK(restored == original);` to
     `CHECK(restored != original);`. Predict whether the CHECK still holds and
     why, then run and restore. Expected: `Check failed`: `CHECK(restored !=
     original);` is false, although the restored value is 1.5. */

  /* Exercise 2: Inspect bytes without type punning: debug a regression
     Worked example 2 now has a line reading `sum -= bytes[i];`. Repair it so
     that the bytes sum to 7 whatever the byte order again. Expected: `Check
     failed` at `sum == 7u` until the line reads `sum += bytes[i];` again. */

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
