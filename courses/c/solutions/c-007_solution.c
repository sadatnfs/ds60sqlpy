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
  /* Compare length and storage */
  {
    char word[] = "cat";
    CHECK(strlen(word) == 3 && sizeof word == 4);
  }

  /* Modify owned text */
  {
    char word[] = "cat";
    word[0] = 'b';
    CHECK(strcmp(word, "bat") == 0);
  }

  /* Detect bounded truncation */
  {
    char out[4];
    int n = snprintf(out, sizeof out, "%s", "hello");
    CHECK(n == 5 && strcmp(out, "hel") == 0);
    CHECK((size_t)n >= sizeof out);
  }

  /* Accept exact capacity */
  {
    char out[4];
    int n = snprintf(out, sizeof out, "%s", "cat");
    CHECK(n == 3 && strcmp(out, "cat") == 0);
  }

  /* Compare content rather than pointers */
  {
    char a[] = "cat";
    char b[] = "cat";
    CHECK(strcmp(a, b) == 0);
  }

  /* Transfer an empty string */
  {
    char empty[1] = {'\0'};
    CHECK(strlen(empty) == 0 && sizeof empty == 1);
  }
  puts("All lesson checks passed.");
  return 0;
}
