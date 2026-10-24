#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void lesson_check(bool condition, const char *file, int line) {
  if (!condition) {
    fprintf(stderr, "Check failed at %s:%d\n", file, line);
    abort();
  }
}
#define CHECK(condition) lesson_check((condition), __FILE__, __LINE__)

_Static_assert(CHAR_BIT == 8, "this octet format requires 8-bit bytes");
static void encode_u32(uint32_t value, unsigned char out[4]) {
  out[0] = (unsigned char)(value >> 24);
  out[1] = (unsigned char)(value >> 16);
  out[2] = (unsigned char)(value >> 8);
  out[3] = (unsigned char)value;
}
static bool decode_u32(const unsigned char *data, size_t n, uint32_t *out) {
  if (n < 4 || data == NULL || out == NULL)
    return false;
  *out = ((uint32_t)data[0] << 24) | ((uint32_t)data[1] << 16) |
         ((uint32_t)data[2] << 8) | (uint32_t)data[3];
  return true;
}

int main(void) {
  /* Encode a known word */
  {
    unsigned char out[4];
    encode_u32(UINT32_C(0x12345678), out);
    CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);
  }

  /* Decode a known word */
  {
    unsigned char data[] = {0, 0, 1, 0};
    uint32_t value = 0;
    CHECK(decode_u32(data, 4, &value) && value == 256);
  }

  /* Reject a truncated field */
  {
    unsigned char data[] = {1, 2, 3};
    uint32_t value = 9;
    CHECK(!decode_u32(data, 3, &value) && value == 9);
  }

  /* Round-trip zero */
  {
    unsigned char out[4];
    encode_u32(0, out);
    uint32_t value = 1;
    CHECK(decode_u32(out, 4, &value) && value == 0);
  }

  /* Round-trip the maximum */
  {
    unsigned char out[4];
    encode_u32(UINT32_MAX, out);
    uint32_t value = 0;
    CHECK(decode_u32(out, 4, &value) && value == UINT32_MAX);
  }

  /* Transfer a framed payload */
  {
    unsigned char frame[] = {1, 0, 0, 0, 7};
    uint32_t value = 0;
    CHECK(frame[0] == 1 && decode_u32(frame + 1, sizeof frame - 1, &value) &&
          value == 7);
  }
  puts("All lesson checks passed.");
  return 0;
}
