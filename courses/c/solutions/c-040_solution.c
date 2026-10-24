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

enum ApiStatus { API_OK, API_TOO_SMALL, API_INVALID };
static enum ApiStatus copy_api(const char *source, char *out, size_t capacity,
                               size_t *required) {
  if (source == NULL || required == NULL)
    return API_INVALID;
  size_t n = strlen(source);
  *required = n;
  if (n == SIZE_MAX || out == NULL || capacity <= n)
    return API_TOO_SMALL;
  memcpy(out, source, n + 1);
  return API_OK;
}
static uint32_t identity_u32(uint32_t value) { return value; }

int main(void) {
  /* Use caller-owned output */
  {
    char out[8];
    size_t required = 0;
    CHECK(copy_api("hello", out, sizeof out, &required) == API_OK);
    CHECK(required == 5 && strcmp(out, "hello") == 0);
  }

  /* Report insufficient capacity */
  {
    char out[4] = "old";
    size_t required = 0;
    CHECK(copy_api("hello", out, sizeof out, &required) == API_TOO_SMALL);
    CHECK(required == 5 && strcmp(out, "old") == 0);
  }

  /* Support a size query */
  {
    size_t required = 0;
    CHECK(copy_api("abc", NULL, 0, &required) == API_TOO_SMALL &&
          required == 3);
  }

  /* Reject a missing required-output pointer */
  {
    char out[4];
    CHECK(copy_api("abc", out, sizeof out, NULL) == API_INVALID);
  }

  /* Keep fixed-width values exact */
  {
    uint32_t value = UINT32_C(0x89abcdef);
    CHECK(identity_u32(value) == value);
  }

  /* Transfer an empty payload */
  {
    char out[1];
    size_t required = 9;
    CHECK(copy_api("", out, sizeof out, &required) == API_OK && required == 0 &&
          out[0] == '\0');
  }
  puts("All lesson checks passed.");
  return 0;
}
