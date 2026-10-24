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

struct Builder {
  char data[16];
  size_t len;
};
static bool append_text(struct Builder *b, const char *source) {
  size_t incoming = strlen(source);
  if (b->len >= sizeof b->data || incoming > sizeof b->data - 1 - b->len)
    return false;
  memcpy(b->data + b->len, source, incoming + 1);
  b->len += incoming;
  return true;
}

int main(void) {
  /* Append two fragments */
  {
    struct Builder b = {0};
    CHECK(append_text(&b, "red") && append_text(&b, " sky"));
    CHECK(b.len == 7 && strcmp(b.data, "red sky") == 0);
  }

  /* Append empty text */
  {
    struct Builder b = {0};
    CHECK(append_text(&b, "abc") && append_text(&b, ""));
    CHECK(b.len == 3 && strcmp(b.data, "abc") == 0);
  }

  /* Fill to exact payload capacity */
  {
    struct Builder b = {0};
    CHECK(append_text(&b, "123456789012345"));
    CHECK(b.len == 15 && b.data[15] == '\0');
  }

  /* Reject one extra character */
  {
    struct Builder b = {0};
    CHECK(append_text(&b, "123456789012345"));
    CHECK(!append_text(&b, "x"));
    CHECK(b.len == 15 && strcmp(b.data, "123456789012345") == 0);
  }

  /* Reject an oversized first fragment */
  {
    struct Builder b = {0};
    CHECK(!append_text(&b, "1234567890123456"));
    CHECK(b.len == 0 && b.data[0] == '\0');
  }

  /* Transfer a delimiter protocol */
  {
    struct Builder b = {0};
    CHECK(append_text(&b, "a") && append_text(&b, ",") &&
          append_text(&b, "b") && append_text(&b, ",") && append_text(&b, "c"));
    CHECK(strcmp(b.data, "a,b,c") == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
