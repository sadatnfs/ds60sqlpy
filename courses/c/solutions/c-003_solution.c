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
  /* Group before calculating */
  {
    CHECK(2 + 3 * 4 == 14);
    CHECK((2 + 3) * 4 == 20);
  }

  /* Use a short-circuit guard */
  {
    int values[1] = {7};
    size_t length = 0;
    bool found = length > 0 && values[0] == 7;
    CHECK(!found);
  }

  /* Sequence updates explicitly */
  {
    int x = 1;
    x += 1;
    int result = x * 2;
    CHECK(x == 2 && result == 4);
  }

  /* Expose signed-unsigned conversion */
  {
    int negative = -1;
    unsigned int positive = 1U;
    CHECK(!((unsigned int)negative < positive));
  }

  /* Choose one conditional branch */
  {
    int zero = 0;
    int value = true ? 7 : 10 / zero;
    CHECK(value == 7);
  }

  /* Transfer assignment diagnosis */
  {
    int x = 0;
    x = 3;
    bool same = (x == 3);
    CHECK(same && x == 3);
  }
  puts("All lesson checks passed.");
  return 0;
}
