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

static int double_value(int value) { return value * 2; }
static int compare_ints(const void *left, const void *right) {
  int a = *(const int *)left, b = *(const int *)right;
  return (a > b) - (a < b);
}
static bool is_even(int value) { return value % 2 == 0; }
static size_t count_if(const int *values, size_t n, bool (*predicate)(int)) {
  size_t count = 0;
  for (size_t i = 0; i < n; i++)
    if (predicate(values[i]))
      count++;
  return count;
}

int main(void) {
  /* Invoke through a function pointer */
  {
    int (*transform)(int) = double_value;
    CHECK(transform(4) == 8);
  }

  /* Sort integers safely */
  {
    int values[] = {3, 1, 2};
    qsort(values, 3, sizeof values[0], compare_ints);
    CHECK(values[0] == 1 && values[1] == 2 && values[2] == 3);
  }

  /* Compare extreme values */
  {
    int a = INT_MIN, b = INT_MAX;
    CHECK(compare_ints(&a, &b) < 0);
  }

  /* Retain equal values */
  {
    int values[] = {2, 1, 2};
    qsort(values, 3, sizeof values[0], compare_ints);
    CHECK(values[0] == 1 && values[1] == 2 && values[2] == 2);
  }

  /* Inject a predicate */
  {
    int values[] = {1, 2, 3, 4};
    CHECK(count_if(values, 4, is_even) == 2);
  }

  /* Transfer an empty callback traversal */
  {
    CHECK(count_if(NULL, 0, is_even) == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
