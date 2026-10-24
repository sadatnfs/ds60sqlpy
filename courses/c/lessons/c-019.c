#include <stdio.h>

int main(void) {
  /* Exercise 1: Encode a known word
     Encode 0x12345678 in big-endian order.
     Expected: The bytes are 12, 34, 56, 78 in hexadecimal. */

  /* Exercise 2: Decode a known word
     Decode bytes 00, 00, 01, 00.
     Expected: The numeric value is 256. */

  /* Exercise 3: Reject a truncated field
     Attempt to decode only three available bytes.
     Expected: The decoder fails and preserves output. */

  /* Exercise 4: Round-trip zero
     Encode and decode numeric zero.
     Expected: The result is zero. */

  /* Exercise 5: Round-trip the maximum
     Encode and decode UINT32_MAX.
     Expected: All bits survive. */

  /* Exercise 6: Transfer a framed payload
     Decode the four bytes after a one-byte version field.
     Expected: Version 1 and payload 7 are interpreted separately. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
