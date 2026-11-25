#include <stdio.h>

int main(void) {
  /* Exercise 1: Encode a known word: predict an edited check
     In worked example 1, change `CHECK(out[0] == 0x12 && out[1] == 0x34 &&
     out[2] == 0x56 && out[3] == 0x78);` to `CHECK(out[1] == 0x12 && out[1] ==
     0x34 && out[2] == 0x56 && out[3] == 0x78);`. Predict whether the CHECK
     still holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] ==
     0x78);` is false, although the bytes are 12, 34, 56, 78 in hexadecimal. */

  /* Exercise 2: Decode a known word: debug a regression
     Worked example 2 now has a line reading `unsigned char data[] = {1, 0, 1,
     0};`. Repair it so that the numeric value is 256 again. Expected: `Check
     failed` at `decode_u32(data, 4, &value) && value == 256` until the line
     reads `unsigned char data[] = {0, 0, 1, 0};` again. */

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
