#ifndef DS60_STATS_H
#define DS60_STATS_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

enum stats_status { STATS_OK, STATS_INVALID, STATS_OVERFLOW };

/*
 * Sum count live integers without modifying them.
 * values may be NULL only when count is zero. out must be non-NULL.
 * On failure, *out is unchanged. On success, the caller retains all ownership.
 */
enum stats_status stats_sum(const int *values, size_t count, int *out);

#ifdef __cplusplus
}
#endif

#endif
