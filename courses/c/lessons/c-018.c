#include <stdio.h>

int main(void) {
  /* Exercise 1: Round-trip an owned stream: predict an edited check
     In worked example 1, change `CHECK(fwrite("abc", 1, 3, f) == 3);` to
     `CHECK(fwrite("abc", 1, 4, f) == 3);`. Predict whether the CHECK still
     holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(fwrite("abc", 1, 4, f) == 3);` is false, although three bytes return
     and match abc. */

  /* Exercise 2: Observe a short read: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(fwrite("ab", 1, 3, f) == 2);`.
     Explain why it fails although two bytes return and EOF becomes set, then
     restore it. Expected: `Check failed` until the CHECK reads
     `CHECK(fwrite("ab", 1, 2, f) == 2);` again, though two bytes return and EOF
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
