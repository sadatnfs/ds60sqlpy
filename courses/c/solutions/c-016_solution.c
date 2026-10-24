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

struct Vector {
  int *data;
  size_t len, cap;
};
static bool vector_reserve(struct Vector *v, size_t cap) {
  if (cap <= v->cap)
    return true;
  if (cap > SIZE_MAX / sizeof *v->data)
    return false;
  int *next = realloc(v->data, cap * sizeof *v->data);
  if (next == NULL)
    return false;
  v->data = next;
  v->cap = cap;
  return true;
}
static bool vector_push(struct Vector *v, int value) {
  if (v->len == v->cap) {
    size_t next = v->cap ? v->cap * 2 : 4;
    if (next < v->cap || !vector_reserve(v, next))
      return false;
  }
  v->data[v->len++] = value;
  return true;
}
static bool vector_pop(struct Vector *v, int *out) {
  if (v->len == 0 || out == NULL)
    return false;
  *out = v->data[--v->len];
  return true;
}
static void vector_destroy(struct Vector *v) {
  free(v->data);
  v->data = NULL;
  v->len = 0;
  v->cap = 0;
}

int main(void) {
  /* Push into an empty vector */
  {
    struct Vector v = {0};
    CHECK(vector_push(&v, 3) && vector_push(&v, 5));
    CHECK(v.len == 2 && v.data[0] == 3 && v.data[1] == 5);
    vector_destroy(&v);
  }

  /* Reserve without adding elements */
  {
    struct Vector v = {0};
    CHECK(vector_reserve(&v, 8));
    CHECK(v.cap >= 8 && v.len == 0);
    vector_destroy(&v);
  }

  /* Grow while preserving contents */
  {
    struct Vector v = {0};
    for (int i = 0; i < 20; i++)
      CHECK(vector_push(&v, i));
    for (size_t i = 0; i < v.len; i++)
      CHECK(v.data[i] == (int)i);
    vector_destroy(&v);
  }

  /* Pop from a nonempty vector */
  {
    struct Vector v = {0};
    int out = 0;
    CHECK(vector_push(&v, 7));
    CHECK(vector_pop(&v, &out) && out == 7 && v.len == 0);
    vector_destroy(&v);
  }

  /* Reject an empty pop */
  {
    struct Vector v = {0};
    int out = 9;
    CHECK(!vector_pop(&v, &out) && out == 9);
    vector_destroy(&v);
  }

  /* Transfer reserve failure atomicity */
  {
    struct Vector v = {0};
    CHECK(vector_push(&v, 4));
    CHECK(!vector_reserve(&v, SIZE_MAX));
    CHECK(v.len == 1 && v.data[0] == 4);
    vector_destroy(&v);
  }
  puts("All lesson checks passed.");
  return 0;
}
