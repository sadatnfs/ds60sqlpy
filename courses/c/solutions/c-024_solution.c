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

static size_t lower_bound(const int *values, size_t n, int target) {
  size_t low = 0, high = n;
  while (low < high) {
    size_t middle = low + (high - low) / 2;
    if (values[middle] < target)
      low = middle + 1;
    else
      high = middle;
  }
  return low;
}

int main(void) {
  /* Find an interior boundary */
  {
    int values[] = {2, 4, 6, 8};
    CHECK(lower_bound(values, 4, 5) == 2);
  }

  /* Find the first duplicate */
  {
    int values[] = {1, 3, 3, 5};
    CHECK(lower_bound(values, 4, 3) == 1);
  }

  /* Handle no larger value */
  {
    int values[] = {2, 4, 6};
    CHECK(lower_bound(values, 3, 9) == 3);
  }

  /* Handle empty input */
  {
    CHECK(lower_bound(NULL, 0, 7) == 0);
  }

  /* Check the first boundary */
  {
    int values[] = {2, 4, 6};
    CHECK(lower_bound(values, 3, 1) == 0);
  }

  /* Transfer an exact membership check */
  {
    int values[] = {2, 4, 6};
    size_t i = lower_bound(values, 3, 4);
    CHECK(i < 3 && values[i] == 4);
  }
  puts("All lesson checks passed.");
  return 0;
}
