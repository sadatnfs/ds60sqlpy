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

static bool add_checked(int a, int b, int *out) {
  if (out == NULL || (b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b))
    return false;
  *out = a + b;
  return true;
}
static bool size_product(size_t a, size_t b, size_t *out) {
  if (out == NULL || (b != 0 && a > SIZE_MAX / b))
    return false;
  *out = a * b;
  return true;
}

int main(void) {
  /* Add ordinary values */
  {
    int out = 0;
    CHECK(add_checked(7, 5, &out) && out == 12);
  }

  /* Reject positive overflow */
  {
    int out = 9;
    CHECK(!add_checked(INT_MAX, 1, &out) && out == 9);
  }

  /* Reject negative overflow */
  {
    int out = 9;
    CHECK(!add_checked(INT_MIN, -1, &out) && out == 9);
  }

  /* Accept exact boundaries */
  {
    int out = 0;
    CHECK(add_checked(INT_MAX, 0, &out) && out == INT_MAX);
    CHECK(add_checked(INT_MIN, 0, &out) && out == INT_MIN);
  }

  /* Reject a size product */
  {
    size_t out = 7;
    CHECK(!size_product(SIZE_MAX, 2, &out) && out == 7);
  }

  /* Transfer the zero product */
  {
    size_t out = 7;
    CHECK(size_product(SIZE_MAX, 0, &out) && out == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
