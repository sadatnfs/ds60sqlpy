#include <stdio.h>

int main(void) {
  /* Exercise 1: Create a trailing payload
     Create a packet containing bytes 1, 2, 3.
     Expected: Length and all three bytes are retained. */

  /* Exercise 2: Create an empty packet
     Create a packet with length zero.
     Expected: The header exists and records zero length. */

  /* Exercise 3: Reject total-size overflow
     Request SIZE_MAX payload bytes.
     Expected: The operation returns NULL before allocation. */

  /* Exercise 4: Clone the complete record
     Create two packets from the same source and mutate one.
     Expected: The other payload remains unchanged. */

  /* Exercise 5: Preserve binary zero
     Store a payload containing a zero byte.
     Expected: Length remains three and the zero is retained. */

  /* Exercise 6: Transfer source independence
     Change the original source after packet construction.
     Expected: The owned packet retains its copied value. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
