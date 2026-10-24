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
  /* Trace a prefix sum */
  {
    int values[] = {2, 4, 6};
    int sum = 0;
    for (size_t i = 0; i < 3; i++) {
      sum += values[i];
    }
    CHECK(sum == 12);
  }

  /* Handle zero iterations */
  {
    int values[1] = {9};
    size_t length = 0;
    int sum = 0;
    for (size_t i = 0; i < length; i++) {
      sum += values[i];
    }
    CHECK(sum == 0);
  }

  /* Find the first match */
  {
    int values[] = {3, 8, 8};
    size_t found = 3;
    for (size_t i = 0; i < 3; i++) {
      if (values[i] == 8) {
        found = i;
        break;
      }
    }
    CHECK(found == 1);
  }

  /* Include an exact threshold */
  {
    int score = 60;
    bool passed = score >= 60;
    CHECK(passed);
  }

  /* Terminate a switch case */
  {
    int code = 2, result = 0;
    switch (code) {
    case 1:
      result = 10;
      break;
    case 2:
      result = 20;
      break;
    default:
      result = -1;
      break;
    }
    CHECK(result == 20);
  }

  /* Transfer reverse traversal safely */
  {
    int values[] = {1, 2, 3};
    int out = 0;
    for (size_t remaining = 3; remaining > 0; remaining--) {
      size_t i = remaining - 1;
      out = out * 10 + values[i];
    }
    CHECK(out == 321);
  }
  puts("All lesson checks passed.");
  return 0;
}
