#include <stdio.h>

int main(void) {
  /* Exercise 1: Swap integer objects: change one input
     Copy worked example 1 into a scratch pad and change `int a = 2, b = 7;` to
     `int a = 3, b = 7;`. Before running, predict which CHECK fails and which
     value it now sees; then run it and restore the original line. Expected: The
     changed run stops with `Check failed` at the CHECK on `a == 7 && b == 2`.
     Restoring the original line brings back the worked observation: the values
     become 7 and 2. */

  /* Exercise 2: Swap fixed byte arrays: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `unsigned char a[] = {2, 2, 3}, b[] = {4, 5, 6};`. Run worked example 2
     with that line, use the failing CHECK to locate the defect and repair it
     without changing the CHECK. Expected: Before the repair the run stops with
     `Check failed` at the CHECK on `a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2]
     == 3`; after it the line reads `unsigned char a[] = {1, 2, 3}, b[] = {4, 5,
     6};` again and their byte contents exchange exactly. */

  /* Exercise 3: Use a zero-length operation
     Invoke the helper with size zero and valid object pointers.
     Expected: Both objects remain unchanged. */

  /* Exercise 4: Round-trip a swap
     Swap two ints twice.
     Expected: The original values return. */

  /* Exercise 5: Read bytes through a generic input
     Count three nonzero bytes in a four-byte buffer.
     Expected: The count is 3. */

  /* Exercise 6: Transfer a typed structure copy
     Copy a Pair into another Pair using its exact size.
     Expected: Both semantic fields match. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
