#include <stdio.h>

int main(void) {
  /* Exercise 1: Round-trip an owned stream
     Write abc, rewind and read three bytes.
     Expected: Three bytes return and match abc. */

  /* Exercise 2: Observe a short read
     Request four bytes from a two-byte stream.
     Expected: Two bytes return and EOF becomes set. */

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
