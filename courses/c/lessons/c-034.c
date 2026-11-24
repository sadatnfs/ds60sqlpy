#include <stdio.h>

int main(void) {
  /* Exercise 1: Transfer a small pipe payload: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(close(fds[0]) ==
     0);` to `CHECK(close(fds[1]) == 0);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: With `CHECK(close(fds[1]) == 0);` the run stops with `Check
     failed` at the CHECK on `close(fds[0]) == 0`, because the "transfer a small
     pipe payload" case no longer shows that three bytes arrive unchanged.
     Restoring `CHECK(close(fds[0]) == 0);` brings that observation back. */

  /* Exercise 2: Observe EOF after closure: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "observe EOF
     after closure" case, so that it reads `CHECK(close(fds[1]) == 0);`. Run the
     example with that line, explain why the edited CHECK now fails even though
     the program state still means read returns zero, and restore it. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `close(fds[0]) == 0`. Once the line reads `CHECK(close(fds[0]) == 0);`
     again, the "observe EOF after closure" case again shows that read returns
     zero. */

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
