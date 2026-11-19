#include <stdio.h>

int main(void) {
  /* Exercise 1: Round-trip an owned stream: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(fwrite("abc", 1,
     3, f) == 3);` to `CHECK(fwrite("abc", 1, 4, f) == 3);` inside its CHECK.
     Before running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: The changed run stops with `Check failed` at the
     CHECK on `fwrite("abc", 1, 3, f) == 3`. Restoring the original line brings
     back the worked observation: three bytes return and match abc. */

  /* Exercise 2: Observe a short read: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(fwrite("ab", 1, 3, f) == 2);`. Run worked example 2 with that line,
     explain why the edited CHECK now fails for the same program state, and
     restore it. Expected: Before the repair the run stops with `Check failed`
     at the CHECK on `fwrite("ab", 1, 2, f) == 2`; after it the line reads
     `CHECK(fwrite("ab", 1, 2, f) == 2);` again and two bytes return and EOF
     becomes set. */

  /* Exercise 3: Avoid prechecking EOF
     Inspect an empty stream before and after a read.
     Expected: EOF is false before the read and true afterward. */

  /* Exercise 4: Read a bounded line
     Read a newline-terminated line into sufficient storage.
     Expected: The newline remains in the result. */

  /* Exercise 5: Clear EOF by rewinding
     Reach EOF, rewind and read the first character again.
     Expected: The first character is available again. */

  /* Exercise 6: Transfer binary zero bytes
     Write and read a byte sequence containing zero.
     Expected: All three bytes survive, including the middle zero. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
