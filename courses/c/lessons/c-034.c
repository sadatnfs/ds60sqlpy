#include <stdio.h>

int main(void) {
  /* Exercise 1: Transfer a small pipe payload
     Write abc, close the writer and read the bytes.
     Expected: Three bytes arrive unchanged. */

  /* Exercise 2: Observe EOF after closure
     Close an unused writer and read from its empty pipe.
     Expected: read returns zero. */

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
