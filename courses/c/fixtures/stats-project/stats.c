#include "stats.h"

#include <limits.h>

enum stats_status stats_sum(const int *values, size_t count, int *out) {
  if (out == NULL || (count != 0 && values == NULL)) {
    return STATS_INVALID;
  }
  int total = 0;
  for (size_t i = 0; i < count; ++i) {
    int value = values[i];
    if ((value > 0 && total > INT_MAX - value) ||
        (value < 0 && total < INT_MIN - value)) {
      return STATS_OVERFLOW;
    }
    total += value;
  }
  *out = total;
  return STATS_OK;
}
