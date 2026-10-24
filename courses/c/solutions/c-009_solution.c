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

int main(void) {
  /* Relate indexing and arithmetic */
  {
    int values[] = {2, 4, 6};
    CHECK(values[1] == *(values + 1) && *(values + 1) == 4);
  }

  /* Measure an array interval */
  {
    int values[] = {2, 4, 6};
    int *begin = values;
    int *end = values + 3;
    ptrdiff_t n = end - begin;
    CHECK(n == 3);
  }

  /* Traverse before the boundary */
  {
    int values[] = {2, 4, 6};
    int sum = 0;
    for (const int *p = values; p != values + 3; p++) {
      sum += *p;
    }
    CHECK(sum == 12);
  }

  /* Construct a subview */
  {
    int values[] = {2, 4, 6};
    const int *view = values + 1;
    size_t n = 2;
    CHECK(n == 2 && view[0] == 4 && view[1] == 6);
  }

  /* Keep an empty boundary non-dereferenced */
  {
    int values[1] = {9};
    const int *begin = values, *end = values;
    size_t visits = 0;
    for (const int *p = begin; p != end; p++) {
      visits++;
    }
    CHECK(visits == 0);
  }

  /* Transfer mutation through a subview */
  {
    int values[] = {1, 2, 3};
    int *suffix = values + 1;
    suffix[0] = 8;
    CHECK(values[1] == 8 && values[0] == 1);
  }
  puts("All lesson checks passed.");
  return 0;
}
