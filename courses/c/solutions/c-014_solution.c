#include <assert.h>
#include <errno.h>
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

static bool parse_int(const char *text, int *out) {
  if (text == NULL || out == NULL)
    return false;
  errno = 0;
  char *end = NULL;
  long value = strtol(text, &end, 10);
  if (end == text || *end != '\0' || errno == ERANGE || value < INT_MIN ||
      value > INT_MAX)
    return false;
  *out = (int)value;
  return true;
}

int main(void) {
  /* Parse a complete integer */
  {
    int out = 0;
    CHECK(parse_int("42", &out) && out == 42);
  }

  /* Reject trailing garbage */
  {
    int out = 7;
    CHECK(!parse_int("42x", &out) && out == 7);
  }

  /* Reject empty input */
  {
    int out = 7;
    CHECK(!parse_int("", &out) && out == 7);
  }

  /* Reject an oversized number */
  {
    int out = 7;
    CHECK(!parse_int("999999999999999999999999999999", &out) && out == 7);
  }

  /* Retain a valid negative value */
  {
    int out = 0;
    CHECK(parse_int("-7", &out) && out == -7);
  }

  /* Transfer the whitespace policy */
  {
    int out = 0;
    CHECK(parse_int(" 3", &out) && out == 3);
    CHECK(!parse_int("3 ", &out));
  }
  puts("All lesson checks passed.");
  return 0;
}
