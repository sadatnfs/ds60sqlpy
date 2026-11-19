#include <stdio.h>

int main(void) {
  /* Exercise 1: Transfer a small pipe payload: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(close(fds[0]) ==
     0);` to `CHECK(close(fds[1]) == 0);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: The changed run stops with `Check failed` at the CHECK on
     `close(fds[0]) == 0`. Restoring the original line brings back the worked
     observation: three bytes arrive unchanged. */

  /* Exercise 2: Observe EOF after closure: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(close(fds[1]) == 0);`. Run worked example 2 with that line, explain
     why the edited CHECK now fails for the same program state, and restore it.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `close(fds[0]) == 0`; after it the line reads `CHECK(close(fds[0]) ==
     0);` again and read returns zero. */

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
