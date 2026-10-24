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

static int twice(int x) { return 2 * x; }
static void reassign(int value) {
  value = 99;
  (void)value;
}
static bool try_area(int w, int h, int *out) {
  if (out == NULL || w <= 0 || h <= 0 || w > INT_MAX / h)
    return false;
  *out = w * h;
  return true;
}

int main(void) {
  /* Call a pure calculation */
  {
    CHECK(twice(7) == 14);
    CHECK(twice(0) == 0);
  }

  /* Return an output on success */
  {
    int out = -1;
    CHECK(try_area(3, 4, &out));
    CHECK(out == 12);
  }

  /* Preserve output on rejection */
  {
    int out = -1;
    CHECK(!try_area(0, 4, &out));
    CHECK(out == -1);
  }

  /* Trace copied scalar state */
  {
    int value = 5;
    reassign(value);
    CHECK(value == 5);
  }

  /* Reject a missing output target */
  {
    CHECK(!try_area(3, 4, NULL));
  }

  /* Transfer overflow prevention */
  {
    int out = 9;
    CHECK(!try_area(INT_MAX, 2, &out));
    CHECK(out == 9);
  }
  puts("All lesson checks passed.");
  return 0;
}
