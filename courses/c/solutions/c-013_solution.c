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

#define SQUARE(x) ((x) * (x))
#define LESSON_CAPACITY 8
#define TYPE_LABEL(x)                                                          \
  _Generic((x), int: "integer", double: "floating", default: "other")
static int square_int(int value) { return value * value; }

int main(void) {
  /* Use a parenthesized macro safely */
  {
    CHECK(SQUARE(2 + 3) == 25);
  }

  /* Prefer a typed helper for mutation */
  {
    int value = 3;
    int result = square_int(value++);
    CHECK(result == 9 && value == 4);
  }

  /* Require a representation fact */
  {
    _Static_assert(sizeof(char) == 1, "char unit must be one");
    CHECK(sizeof(char) == 1);
  }

  /* Read a configuration constant */
  {
    int values[LESSON_CAPACITY] = {0};
    CHECK(sizeof values / sizeof values[0] == 8);
  }

  /* Select by a simple type */
  {
    CHECK(strcmp(TYPE_LABEL(3), "integer") == 0);
    CHECK(strcmp(TYPE_LABEL(3.0), "floating") == 0);
  }

  /* Transfer an inline-style function contract */
  {
    CHECK(square_int(0) == 0 && square_int(-3) == 9);
  }
  puts("All lesson checks passed.");
  return 0;
}
