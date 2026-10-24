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

static int sum_items(const int *values, size_t n) {
  int out = 0;
  for (size_t i = 0; i < n; i++)
    out += values[i];
  return out;
}

int main(void) {
  /* Derive a local element count */
  {
    int values[] = {2, 4, 6};
    size_t n = sizeof values / sizeof values[0];
    CHECK(n == 3);
  }

  /* Pass an explicit length */
  {
    int values[] = {2, 4, 6};
    CHECK(sum_items(values, 3) == 12);
  }

  /* Inspect partial initialization */
  {
    int values[3] = {7};
    CHECK(values[0] == 7 && values[1] == 0 && values[2] == 0);
  }

  /* Use a logical prefix */
  {
    int values[] = {2, 4, 99};
    CHECK(sum_items(values, 2) == 6);
  }

  /* Handle an empty logical view */
  {
    CHECK(sum_items(NULL, 0) == 0);
  }

  /* Transfer independent array storage */
  {
    int a[] = {1, 2};
    int b[2];
    for (size_t i = 0; i < 2; i++)
      b[i] = a[i];
    b[0] = 9;
    CHECK(a[0] == 1 && b[0] == 9);
  }
  puts("All lesson checks passed.");
  return 0;
}
