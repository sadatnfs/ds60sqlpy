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

static int read_sum(const int *values, size_t n) {
  int sum = 0;
  for (size_t i = 0; i < n; i++)
    sum += values[i];
  return sum;
}

int main(void) {
  /* Read through a const view */
  {
    int value = 4;
    const int *view = &value;
    CHECK(*view == 4);
  }

  /* Observe another valid mutation */
  {
    int value = 4;
    const int *view = &value;
    value = 7;
    CHECK(*view == 7);
  }

  /* Use a fixed pointer target */
  {
    int value = 1;
    int *const fixed = &value;
    *fixed = 8;
    CHECK(value == 8);
  }

  /* Read an immutable object */
  {
    const int value = 9;
    const int *p = &value;
    CHECK(*p == 9);
  }

  /* Pass a read-only array contract */
  {
    const int values[] = {1, 2, 3};
    CHECK(read_sum(values, 3) == 6);
  }

  /* Transfer snapshot independence */
  {
    int value = 2;
    const int *view = &value;
    int snapshot = *view;
    value = 5;
    CHECK(snapshot == 2 && *view == 5);
  }
  puts("All lesson checks passed.");
  return 0;
}
