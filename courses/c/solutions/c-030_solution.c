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

static bool at_index(const int *values, size_t n, size_t i, int *out) {
  if (values == NULL || out == NULL || i >= n)
    return false;
  *out = values[i];
  return true;
}

int main(void) {
  /* Guard a formerly unsafe index */
  {
    int values[] = {2, 4, 6}, out = 0;
    CHECK(at_index(values, 3, 2, &out) && out == 6);
  }

  /* Reject the one-past index */
  {
    int values[] = {2, 4, 6}, out = 9;
    CHECK(!at_index(values, 3, 3, &out) && out == 9);
  }

  /* Reject an empty view */
  {
    int out = 9;
    CHECK(!at_index(NULL, 0, 0, &out) && out == 9);
  }

  /* Verify a valid allocation lifetime */
  {
    int *p = malloc(sizeof *p);
    CHECK(p != NULL);
    *p = 7;
    CHECK(*p == 7);
    free(p);
    p = NULL;
    CHECK(p == NULL);
  }

  /* Retain output capacity checks */
  {
    char out[8];
    int n = snprintf(out, sizeof out, "%s", "ready");
    CHECK(n >= 0 && (size_t)n < sizeof out && strcmp(out, "ready") == 0);
  }

  /* Transfer a newly discovered boundary */
  {
    int values[] = {5}, out = 0;
    CHECK(at_index(values, 1, 0, &out) && out == 5);
    CHECK(!at_index(values, 1, 1, &out));
  }
  puts("All lesson checks passed.");
  return 0;
}
