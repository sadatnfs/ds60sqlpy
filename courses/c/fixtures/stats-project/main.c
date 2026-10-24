#include "stats.h"

#include <stdio.h>
#include <stdlib.h>

int main(void) {
  const int values[] = {2, 4, 6};
  int total = 0;
  enum stats_status status =
      stats_sum(values, sizeof values / sizeof values[0], &total);
  if (status != STATS_OK) {
    fputs("The checked sum could not be produced.\n", stderr);
    return EXIT_FAILURE;
  }
  printf("total=%d\n", total);
  return EXIT_SUCCESS;
}
