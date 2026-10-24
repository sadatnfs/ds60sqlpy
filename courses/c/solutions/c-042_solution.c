#include <assert.h>
#include <errno.h>
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

struct Summary {
  size_t rows;
  unsigned total;
};
static bool parse_record(const char *line, unsigned *out) {
  if (line == NULL || out == NULL)
    return false;
  const char *comma = strchr(line, ',');
  if (comma == NULL || comma == line || (size_t)(comma - line) > 15 ||
      strchr(comma + 1, ',') != NULL)
    return false;
  for (const char *p = line; p < comma; p++)
    if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z')))
      return false;
  if (comma[1] < '0' || comma[1] > '9')
    return false;
  errno = 0;
  char *end = NULL;
  unsigned long value = strtoul(comma + 1, &end, 10);
  if (errno == ERANGE || *end != '\0' || value > UINT_MAX)
    return false;
  *out = (unsigned)value;
  return true;
}
static bool summarize(const char *const *rows, size_t count,
                      struct Summary *out) {
  if (out == NULL || (count > 0 && rows == NULL) || count > 100)
    return false;
  struct Summary staged = {0};
  for (size_t i = 0; i < count; i++) {
    unsigned value = 0;
    if (!parse_record(rows[i], &value) || value > UINT_MAX - staged.total)
      return false;
    staged.total += value;
    staged.rows++;
  }
  *out = staged;
  return true;
}

int main(void) {
  /* Summarize valid records */
  {
    const char *rows[] = {"alpha,3", "beta,4"};
    struct Summary out = {0};
    CHECK(summarize(rows, 2, &out) && out.rows == 2 && out.total == 7);
  }

  /* Reject a malformed record */
  {
    const char *rows[] = {"alpha,3", "beta,-1"};
    struct Summary out = {9, 99};
    CHECK(!summarize(rows, 2, &out) && out.rows == 9 && out.total == 99);
  }

  /* Handle an empty batch */
  {
    struct Summary out = {9, 99};
    CHECK(summarize(NULL, 0, &out) && out.rows == 0 && out.total == 0);
  }

  /* Reject extra field syntax */
  {
    unsigned value = 0;
    CHECK(!parse_record("alpha,3,extra", &value));
  }

  /* Preserve a legitimate zero */
  {
    const char *rows[] = {"alpha,0"};
    struct Summary out = {0};
    CHECK(summarize(rows, 1, &out) && out.rows == 1 && out.total == 0);
  }

  /* Transfer repeatable recovery */
  {
    const char *bad[] = {"x,bad"}, *good[] = {"x,8"};
    struct Summary out = {0};
    CHECK(!summarize(bad, 1, &out));
    CHECK(summarize(good, 1, &out) && out.rows == 1 && out.total == 8);
  }
  puts("All lesson checks passed.");
  return 0;
}
