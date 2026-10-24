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

static int *allocate_ints(size_t count) {
  if (count == 0 || count > SIZE_MAX / sizeof(int))
    return NULL;
  return malloc(count * sizeof(int));
}

int main(void) {
  /* Allocate and initialize */
  {
    int *p = allocate_ints(3);
    CHECK(p != NULL);
    p[0] = 2;
    p[1] = 4;
    p[2] = 6;
    CHECK(p[0] + p[1] + p[2] == 12);
    free(p);
  }

  /* Inspect zero-initialized integers */
  {
    int *p = calloc(3, sizeof *p);
    CHECK(p != NULL);
    CHECK(p[0] == 0 && p[1] == 0 && p[2] == 0);
    free(p);
  }

  /* Define the empty allocation policy */
  {
    CHECK(allocate_ints(0) == NULL);
  }

  /* Reject multiplication overflow */
  {
    CHECK(allocate_ints(SIZE_MAX) == NULL);
  }

  /* Release an absent allocation */
  {
    int *p = NULL;
    free(p);
    CHECK(p == NULL);
  }

  /* Transfer ownership cleanup */
  {
    int *p = allocate_ints(1);
    CHECK(p != NULL);
    *p = 9;
    CHECK(*p == 9);
    free(p);
    p = NULL;
    CHECK(p == NULL);
  }
  puts("All lesson checks passed.");
  return 0;
}
