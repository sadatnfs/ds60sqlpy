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

static bool parse_list(const char *text, unsigned *out, size_t capacity,
                       size_t *count) {
  if (text == NULL || out == NULL || count == NULL)
    return false;
  unsigned temporary[8];
  size_t used = 0;
  unsigned value = 0;
  bool digit_seen = false;
  for (const unsigned char *p = (const unsigned char *)text;; p++) {
    unsigned char c = *p;
    if (c >= '0' && c <= '9') {
      unsigned digit = (unsigned)(c - '0');
      if (value > (UINT_MAX - digit) / 10U)
        return false;
      value = value * 10U + digit;
      digit_seen = true;
    } else if (c == ',' || c == '\0') {
      if (!digit_seen || used >= 8 || used >= capacity)
        return false;
      temporary[used++] = value;
      if (c == '\0')
        break;
      value = 0;
      digit_seen = false;
    } else {
      return false;
    }
  }
  memcpy(out, temporary, used * sizeof temporary[0]);
  *count = used;
  return true;
}

int main(void) {
  /* Parse a valid list */
  {
    unsigned out[3] = {0};
    size_t count = 0;
    CHECK(parse_list("1,20,3", out, 3, &count) && count == 3 && out[0] == 1 &&
          out[1] == 20 && out[2] == 3);
  }

  /* Reject an empty field */
  {
    unsigned out[3] = {9, 9, 9};
    size_t count = 7;
    CHECK(!parse_list("1,,3", out, 3, &count) && out[0] == 9 && count == 7);
  }

  /* Reject a trailing separator */
  {
    unsigned out[3] = {0};
    size_t count = 0;
    CHECK(!parse_list("1,2,", out, 3, &count));
  }

  /* Enforce output capacity */
  {
    unsigned out[2] = {9, 9};
    size_t count = 7;
    CHECK(!parse_list("1,2,3", out, 2, &count) && out[0] == 9 && count == 7);
  }

  /* Reject numeric overflow */
  {
    unsigned out[1] = {0};
    size_t count = 0;
    CHECK(!parse_list("999999999999999999999999", out, 1, &count));
  }

  /* Transfer exact grammar boundaries */
  {
    unsigned out[1] = {9};
    size_t count = 0;
    CHECK(parse_list("0", out, 1, &count) && out[0] == 0 && count == 1);
    CHECK(!parse_list(" 1", out, 1, &count));
  }
  puts("All lesson checks passed.");
  return 0;
}
