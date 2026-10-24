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

static int seven(void) { return 7; }

int main(void) {
  /* Check a first value */
  {
    int total = 2 + 3;
    CHECK(total == 5);
  }

  /* Format a checked result */
  {
    char out[16];
    int n = snprintf(out, sizeof out, "total=%d", 5);
    CHECK(n == 7);
    CHECK(strcmp(out, "total=5") == 0);
  }

  /* Trace statement order */
  {
    int count = 1;
    count += 1;
    count *= 3;
    CHECK(count == 6);
  }

  /* Inspect a boolean condition */
  {
    bool same = (4 == 4);
    bool different = (4 != 5);
    CHECK(same && different);
  }

  /* Use an explicit return contract */
  {
    CHECK(seven() == 7);
  }

  /* Transfer a receipt calculation */
  {
    int items = 4;
    int unit = 6;
    int amount = items * unit;
    CHECK(amount == 24);
  }
  puts("All lesson checks passed.");
  return 0;
}
