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

enum { TABLE_CAPACITY = 8 };
struct Entry {
  bool used;
  unsigned key;
  int value;
};
struct Table {
  struct Entry entries[TABLE_CAPACITY];
};
static bool table_put(struct Table *t, unsigned key, int value) {
  for (size_t step = 0; step < TABLE_CAPACITY; step++) {
    size_t i = (key % TABLE_CAPACITY + step) % TABLE_CAPACITY;
    struct Entry *e = &t->entries[i];
    if (!e->used || e->key == key) {
      e->used = true;
      e->key = key;
      e->value = value;
      return true;
    }
  }
  return false;
}
static bool table_get(const struct Table *t, unsigned key, int *out) {
  for (size_t step = 0; step < TABLE_CAPACITY; step++) {
    size_t i = (key % TABLE_CAPACITY + step) % TABLE_CAPACITY;
    const struct Entry *e = &t->entries[i];
    if (!e->used)
      return false;
    if (e->key == key) {
      *out = e->value;
      return true;
    }
  }
  return false;
}

int main(void) {
  /* Insert and retrieve */
  {
    struct Table t = {0};
    int out = 0;
    CHECK(table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7);
  }

  /* Resolve a collision */
  {
    struct Table t = {0};
    int out = 0;
    CHECK(table_put(&t, 1, 10) && table_put(&t, 9, 90));
    CHECK(table_get(&t, 1, &out) && out == 10);
    CHECK(table_get(&t, 9, &out) && out == 90);
  }

  /* Replace an existing key */
  {
    struct Table t = {0};
    int out = 0;
    CHECK(table_put(&t, 2, 3) && table_put(&t, 2, 8));
    CHECK(table_get(&t, 2, &out) && out == 8);
  }

  /* Distinguish absent from zero */
  {
    struct Table t = {0};
    int out = 9;
    CHECK(table_put(&t, 0, 0) && table_get(&t, 0, &out) && out == 0);
    out = 9;
    CHECK(!table_get(&t, 3, &out) && out == 9);
  }

  /* Reject a full-table insertion */
  {
    struct Table t = {0};
    for (unsigned i = 0; i < 8; i++)
      CHECK(table_put(&t, i, (int)i));
    CHECK(!table_put(&t, 99, 99));
  }

  /* Transfer replacement while full */
  {
    struct Table t = {0};
    for (unsigned i = 0; i < 8; i++)
      CHECK(table_put(&t, i, (int)i));
    int out = 0;
    CHECK(table_put(&t, 3, 30) && table_get(&t, 3, &out) && out == 30);
  }
  puts("All lesson checks passed.");
  return 0;
}
