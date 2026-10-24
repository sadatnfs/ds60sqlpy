#include "stats.h"

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static void require_true(int condition, int line) {
  if (!condition) {
    fprintf(stderr, "API test failed at line %d\n", line);
    abort();
  }
}
#define CHECK(condition) require_true((condition), __LINE__)

int main(void) {
  int out = 9;
  const int values[] = {2, 4, 6};
  CHECK(stats_sum(values, 3, &out) == STATS_OK && out == 12);
  CHECK(values[0] == 2 && values[2] == 6);

  CHECK(stats_sum(NULL, 0, &out) == STATS_OK && out == 0);
  out = 9;
  CHECK(stats_sum(NULL, 1, &out) == STATS_INVALID && out == 9);
  CHECK(stats_sum(values, 3, NULL) == STATS_INVALID);

  const int overflow[] = {INT_MAX, 1};
  CHECK(stats_sum(overflow, 2, &out) == STATS_OVERFLOW && out == 9);
  const int underflow[] = {INT_MIN, -1};
  CHECK(stats_sum(underflow, 2, &out) == STATS_OVERFLOW && out == 9);

  const int boundary[] = {INT_MAX, -1};
  CHECK(stats_sum(boundary, 2, &out) == STATS_OK && out == INT_MAX - 1);
  const int negative[] = {-2, -4};
  CHECK(stats_sum(negative, 2, &out) == STATS_OK && out == -6);

  puts("All multi-file API checks passed.");
  return 0;
}
