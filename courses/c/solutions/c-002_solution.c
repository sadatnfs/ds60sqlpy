#include <assert.h>
#include <limits.h>
#include <math.h>
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
  /* Compare integer and floating division */
  {
    int whole = 7 / 2;
    double fraction = 7 / 2.0;
    CHECK(whole == 3 && fraction == 3.5);
  }

  /* Observe defined unsigned wrap */
  {
    unsigned int n = UINT_MAX;
    n += 1U;
    CHECK(n == 0U);
  }

  /* Inspect representation facts */
  {
    CHECK(sizeof(char) == 1);
    CHECK(CHAR_BIT >= 8);
  }

  /* Widen before multiplication */
  {
    int64_t a = 50000;
    int64_t b = 50000;
    CHECK(a * b == INT64_C(2500000000));
  }

  /* Check a tiny floating calculation */
  {
    double a = 0.1, b = 0.2;
    CHECK(fabs((a + b) - 0.3) < 1e-15);
  }

  /* Transfer negative division */
  {
    int q = -7 / 2, r = -7 % 2;
    CHECK(q == -3 && r == -1 && q * 2 + r == -7);
  }
  puts("All lesson checks passed.");
  return 0;
}
