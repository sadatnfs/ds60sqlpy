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

static void increment(int *p) { *p += 1; }
static bool set_if_present(int *p, int value) {
  if (p == NULL)
    return false;
  *p = value;
  return true;
}
static void swap_ints(int *a, int *b) {
  int saved = *a;
  *a = *b;
  *b = saved;
}

int main(void) {
  /* Change a caller-owned value */
  {
    int n = 4;
    increment(&n);
    CHECK(n == 5);
  }

  /* Read a target copy */
  {
    int n = 3;
    int *p = &n;
    int copy = *p;
    *p = 9;
    CHECK(copy == 3 && n == 9);
  }

  /* Reject an absent target */
  {
    CHECK(!set_if_present(NULL, 8));
  }

  /* Update a present target */
  {
    int n = 1;
    CHECK(set_if_present(&n, 8) && n == 8);
  }

  /* Distinguish pointer and target change */
  {
    int a = 2, b = 7;
    int *p = &a;
    p = &b;
    CHECK(a == 2 && b == 7 && *p == 7);
  }

  /* Transfer a swap contract */
  {
    int a = 2, b = 7;
    swap_ints(&a, &b);
    CHECK(a == 7 && b == 2);
  }
  puts("All lesson checks passed.");
  return 0;
}
