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
  /* Copy a representation safely */
  {
    float original = 1.5f, restored = 0.0f;
    unsigned char bytes[sizeof original];
    memcpy(bytes, &original, sizeof original);
    memcpy(&restored, bytes, sizeof restored);
    CHECK(restored == original);
  }

  /* Inspect bytes without type punning */
  {
    int value = 7;
    const unsigned char *bytes = (const unsigned char *)&value;
    unsigned int sum = 0;
    for (size_t i = 0; i < sizeof value; i++)
      sum += bytes[i];
    CHECK(sizeof value >= 1);
    (void)sum;
  }

  /* Handle overlapping moves */
  {
    char text[8] = "abc";
    memmove(text + 1, text, 4);
    CHECK(strcmp(text, "aabc") == 0);
  }

  /* Keep typed access in a real object */
  {
    int source = 9, target = 0;
    memcpy(&target, &source, sizeof target);
    CHECK(target == 9);
  }

  /* Inspect an alignment requirement */
  {
    CHECK(_Alignof(int) > 0 && _Alignof(max_align_t) > 0);
  }

  /* Transfer a bounded byte copy */
  {
    unsigned char source[4] = {0, 1, 2, 255}, target[4] = {0};
    memcpy(target, source, sizeof source);
    CHECK(memcmp(source, target, sizeof source) == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
