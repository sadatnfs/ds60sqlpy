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

struct Pair {
  int x, y;
};
static void swap_bytes(void *left, void *right, size_t size) {
  unsigned char *a = left, *b = right;
  for (size_t i = 0; i < size; i++) {
    unsigned char saved = a[i];
    a[i] = b[i];
    b[i] = saved;
  }
}
static size_t count_nonzero(const void *data, size_t size) {
  const unsigned char *bytes = data;
  size_t count = 0;
  for (size_t i = 0; i < size; i++)
    if (bytes[i] != 0)
      count++;
  return count;
}

int main(void) {
  /* Swap integer objects */
  {
    int a = 2, b = 7;
    swap_bytes(&a, &b, sizeof a);
    CHECK(a == 7 && b == 2);
  }

  /* Swap fixed byte arrays */
  {
    unsigned char a[] = {1, 2, 3}, b[] = {4, 5, 6};
    swap_bytes(a, b, sizeof a);
    CHECK(a[0] == 4 && a[2] == 6 && b[0] == 1 && b[2] == 3);
  }

  /* Use a zero-length operation */
  {
    int a = 2, b = 7;
    swap_bytes(&a, &b, 0);
    CHECK(a == 2 && b == 7);
  }

  /* Round-trip a swap */
  {
    int a = 2, b = 7;
    swap_bytes(&a, &b, sizeof a);
    swap_bytes(&a, &b, sizeof a);
    CHECK(a == 2 && b == 7);
  }

  /* Read bytes through a generic input */
  {
    unsigned char data[] = {1, 0, 2, 3};
    CHECK(count_nonzero(data, sizeof data) == 3);
  }

  /* Transfer a typed structure copy */
  {
    struct Pair a = {2, 3}, b = {0, 0};
    memcpy(&b, &a, sizeof b);
    CHECK(b.x == 2 && b.y == 3);
  }
  puts("All lesson checks passed.");
  return 0;
}
