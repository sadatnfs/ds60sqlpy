#include <stdio.h>

int main(void) {
  /* Exercise 1: Transfer a small pipe payload: predict an edited check
     In worked example 1, change `CHECK(close(fds[0]) == 0);` to
     `CHECK(close(fds[1]) == 0);`. Predict whether the CHECK still holds and
     why, then run and restore. Expected: `Check failed`: `CHECK(close(fds[1])
     == 0);` is false, although three bytes arrive unchanged. */

  /* Exercise 2: Observe EOF after closure: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(close(fds[1]) == 0);`. Explain
     why it fails although read returns zero, then restore it. Expected: `Check
     failed` until the CHECK reads `CHECK(close(fds[0]) == 0);` again, though
     read returns zero. */

  /* Exercise 3: Read a payload in two pieces
     Write four bytes and request two bytes at a time.
     Expected: The pieces are ab and cd. */

  /* Exercise 4: Retain binary zeros
     Send bytes 1, 0, 2 through a pipe.
     Expected: All three bytes are preserved. */

  /* Exercise 5: Account for duplicated ownership
     Duplicate the write descriptor, then close both before reading EOF.
     Expected: EOF arrives after both references close. */

  /* Exercise 6: Transfer a bounded record decoder
     Read exactly a two-byte tag from a three-byte payload.
     Expected: The tag is OK and one byte remains for the next read. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
