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

struct Point {
  int x, y;
};

int main(void) {
  /* Sum one field in records */
  {
    struct Point records[] = {{1, 10}, {2, 20}, {3, 30}};
    int sum = 0;
    for (size_t i = 0; i < 3; i++)
      sum += records[i].x;
    CHECK(sum == 6);
  }

  /* Compute the same result by columns */
  {
    int x[] = {1, 2, 3};
    int y[] = {10, 20, 30};
    int sum = 0;
    for (size_t i = 0; i < 3; i++)
      sum += x[i];
    CHECK(sum == 6 && y[2] == 30);
  }

  /* Inspect legal field offsets */
  {
    CHECK(offsetof(struct Point, x) < sizeof(struct Point));
    CHECK(offsetof(struct Point, y) > offsetof(struct Point, x));
  }

  /* Count algorithmic work */
  {
    int values[] = {1, 2, 3, 4, 5, 6};
    size_t visits = 0;
    int sum = 0;
    for (size_t i = 0; i < 6; i++) {
      visits++;
      sum += values[i];
    }
    CHECK(visits == 6 && sum == 21);
  }

  /* Preserve result under blocking */
  {
    int values[] = {1, 2, 3, 4, 5, 6};
    int sum = 0;
    for (size_t block = 0; block < 6; block += 2)
      for (size_t i = block; i < block + 2; i++)
        sum += values[i];
    CHECK(sum == 21);
  }

  /* Transfer a partial block */
  {
    int values[] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (size_t block = 0; block < 5; block += 2) {
      size_t end = block + 2;
      if (end > 5)
        end = 5;
      for (size_t i = block; i < end; i++)
        sum += values[i];
    }
    CHECK(sum == 15);
  }
  puts("All lesson checks passed.");
  return 0;
}
