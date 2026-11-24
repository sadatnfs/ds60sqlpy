#include <stdio.h>

int main(void) {
  /* Exercise 1: Encode a known word: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(out[0] == 0x12
     && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` to `CHECK(out[1]
     == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` inside its
     CHECK. Before running, predict whether the CHECK still holds and explain
     why; then restore it. Expected: With `CHECK(out[1] == 0x12 && out[1] ==
     0x34 && out[2] == 0x56 && out[3] == 0x78);` the run stops with `Check
     failed` at the CHECK on `out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56
     && out[3] == 0x78`, because the "encode a known word" case no longer shows
     that the bytes are 12, 34, 56, 78 in hexadecimal. Restoring `CHECK(out[0]
     == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` brings
     that observation back. */

  /* Exercise 2: Decode a known word: debug a regression
     A regression changed one token in worked example 2, the "decode a known
     word" case, so one line now reads `unsigned char data[] = {1, 0, 1, 0};`.
     Run the example with that line, use the failing CHECK to find why the
     numeric value is 256 no longer holds and repair the line without changing
     the CHECK. Expected: Before the repair the run stops with `Check failed` at
     the CHECK on `decode_u32(data, 4, &value) && value == 256`. Once the line
     reads `unsigned char data[] = {0, 0, 1, 0};` again, the "decode a known
     word" case again shows that the numeric value is 256. */

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
