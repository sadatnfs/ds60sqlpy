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

struct Text {
  char *data;
  size_t len;
};
static bool text_create(struct Text *out, const char *source) {
  if (out == NULL || source == NULL || out->data != NULL)
    return false;
  size_t n = strlen(source);
  if (n == SIZE_MAX)
    return false;
  char *data = malloc(n + 1);
  if (data == NULL)
    return false;
  memcpy(data, source, n + 1);
  out->data = data;
  out->len = n;
  return true;
}
static void text_destroy(struct Text *t) {
  free(t->data);
  t->data = NULL;
  t->len = 0;
}

int main(void) {
  /* Create an owned string */
  {
    struct Text t = {0};
    CHECK(text_create(&t, "alpha"));
    CHECK(t.len == 5 && strcmp(t.data, "alpha") == 0);
    text_destroy(&t);
  }

  /* Clone independent storage */
  {
    struct Text a = {0}, b = {0};
    CHECK(text_create(&a, "cat") && text_create(&b, a.data));
    b.data[0] = 'b';
    CHECK(strcmp(a.data, "cat") == 0 && strcmp(b.data, "bat") == 0);
    text_destroy(&a);
    text_destroy(&b);
  }

  /* Borrow without releasing */
  {
    struct Text t = {0};
    CHECK(text_create(&t, "ready"));
    const char *view = t.data;
    CHECK(strcmp(view, "ready") == 0);
    text_destroy(&t);
  }

  /* Represent an owned empty string */
  {
    struct Text t = {0};
    CHECK(text_create(&t, ""));
    CHECK(t.len == 0 && t.data != NULL && t.data[0] == '\0');
    text_destroy(&t);
  }

  /* Make cleanup idempotent */
  {
    struct Text t = {0};
    CHECK(text_create(&t, "x"));
    text_destroy(&t);
    text_destroy(&t);
    CHECK(t.data == NULL && t.len == 0);
  }

  /* Transfer a deliberate move */
  {
    struct Text source = {0};
    CHECK(text_create(&source, "move"));
    struct Text destination = source;
    source = (struct Text){0};
    CHECK(source.data == NULL && strcmp(destination.data, "move") == 0);
    text_destroy(&destination);
  }
  puts("All lesson checks passed.");
  return 0;
}
