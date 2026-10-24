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

static bool fail_allocation = false;
static void *controlled_alloc(size_t size) {
  return fail_allocation ? NULL : malloc(size);
}
static bool copy_with_allocator(const char *source, char **out,
                                void *(*allocate)(size_t)) {
  size_t n = strlen(source);
  if (n == SIZE_MAX)
    return false;
  char *copy = allocate(n + 1);
  if (copy == NULL)
    return false;
  memcpy(copy, source, n + 1);
  *out = copy;
  return true;
}

int main(void) {
  /* Exercise successful allocation */
  {
    char *out = NULL;
    fail_allocation = false;
    CHECK(copy_with_allocator("abc", &out, controlled_alloc));
    CHECK(strcmp(out, "abc") == 0);
    free(out);
  }

  /* Inject allocation failure */
  {
    char *out = NULL;
    fail_allocation = true;
    CHECK(!copy_with_allocator("abc", &out, controlled_alloc));
    CHECK(out == NULL);
    fail_allocation = false;
  }

  /* Preserve an existing output pointer */
  {
    char existing[] = "old";
    char *out = existing;
    fail_allocation = true;
    CHECK(!copy_with_allocator("new", &out, controlled_alloc));
    CHECK(out == existing && strcmp(out, "old") == 0);
    fail_allocation = false;
  }

  /* Test an empty valid input */
  {
    char *out = NULL;
    CHECK(copy_with_allocator("", &out, controlled_alloc));
    CHECK(out != NULL && out[0] == '\0');
    free(out);
  }

  /* Retain a normal case after failure */
  {
    char *out = NULL;
    fail_allocation = true;
    CHECK(!copy_with_allocator("x", &out, controlled_alloc));
    fail_allocation = false;
    CHECK(copy_with_allocator("x", &out, controlled_alloc));
    CHECK(strcmp(out, "x") == 0);
    free(out);
  }

  /* Transfer a distinguishing content check */
  {
    char *out = NULL;
    CHECK(copy_with_allocator("Red", &out, controlled_alloc));
    CHECK(strcmp(out, "Red") == 0 && strcmp(out, "red") != 0);
    free(out);
  }
  puts("All lesson checks passed.");
  return 0;
}
