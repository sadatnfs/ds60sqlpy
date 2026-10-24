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

static int stats_sum(const int *values, size_t length);
static int stats_sum(const int *values, size_t length) {
  int sum = 0;
  for (size_t i = 0; i < length; i++)
    sum += values[i];
  return sum;
}

int main(void) {
  /* Call a declared API */
  {
    int values[] = {2, 4, 6};
    CHECK(stats_sum(values, 3) == 12);
  }

  /* Use an empty API contract */
  {
    CHECK(stats_sum(NULL, 0) == 0);
  }

  /* Compare two callers */
  {
    int a[] = {1, 2}, b[] = {3, 4};
    CHECK(stats_sum(a, 2) == 3 && stats_sum(b, 2) == 7);
  }

  /* Retain caller data */
  {
    int values[] = {2, 4};
    (void)stats_sum(values, 2);
    CHECK(values[0] == 2 && values[1] == 4);
  }

  /* Check a one-element boundary */
  {
    int values[] = {-3};
    CHECK(stats_sum(values, 1) == -3);
  }

  /* Transfer repeatable builds to repeatable behavior */
  {
    int values[] = {1, 2, 3};
    int first = stats_sum(values, 3), second = stats_sum(values, 3);
    CHECK(first == 6 && second == 6);
  }
  puts("All lesson checks passed.");
  return 0;
}
