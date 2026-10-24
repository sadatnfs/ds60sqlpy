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
enum ValueTag { VALUE_INT, VALUE_TEXT };
struct Value {
  enum ValueTag tag;
  union {
    int integer;
    const char *text;
  } data;
};
static bool valid_tag(enum ValueTag tag) {
  return tag == VALUE_INT || tag == VALUE_TEXT;
}

int main(void) {
  /* Use named fields */
  {
    struct Point p = {.x = 2, .y = 3};
    CHECK(p.x + p.y == 5);
  }

  /* Copy scalar fields */
  {
    struct Point a = {2, 3};
    struct Point b = a;
    b.x = 9;
    CHECK(a.x == 2 && b.x == 9);
  }

  /* Interpret an integer alternative */
  {
    struct Value v = {.tag = VALUE_INT, .data.integer = 7};
    CHECK(v.tag == VALUE_INT && v.data.integer == 7);
  }

  /* Interpret a text alternative */
  {
    struct Value v = {.tag = VALUE_TEXT, .data.text = "ready"};
    CHECK(v.tag == VALUE_TEXT && strcmp(v.data.text, "ready") == 0);
  }

  /* Compare semantic fields */
  {
    struct Point a = {2, 3}, b = {2, 3};
    CHECK(a.x == b.x && a.y == b.y);
  }

  /* Transfer invalid-tag diagnosis */
  {
    CHECK(!valid_tag((enum ValueTag)99));
  }
  puts("All lesson checks passed.");
  return 0;
}
