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

static int next_count(void) {
  static int count = 0;
  count++;
  return count;
}
static const int *static_value(void) {
  static const int value = 7;
  return &value;
}
static int local_count(void) {
  int count = 0;
  count++;
  return count;
}

int main(void) {
  /* Trace block shadowing */
  {
    int value = 3;
    {
      int value = 7;
      CHECK(value == 7);
    }
    CHECK(value == 3);
  }

  /* Retain static state */
  {
    CHECK(next_count() == 1);
    CHECK(next_count() == 2);
  }

  /* Return a static address */
  {
    const int *p = static_value();
    CHECK(*p == 7);
  }

  /* Keep automatic state per call */
  {
    CHECK(local_count() == 1 && local_count() == 1);
  }

  /* Separate visibility from lifetime */
  {
    int copy = 0;
    {
      int local = 9;
      copy = local;
    }
    CHECK(copy == 9);
  }

  /* Transfer initialized aggregation */
  {
    int total = 0;
    size_t count = 0;
    for (size_t i = 0; i < count; i++)
      total += (int)i;
    CHECK(total == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
