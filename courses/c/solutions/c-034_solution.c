#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

static void lesson_check(bool condition, const char *file, int line) {
  if (!condition) {
    fprintf(stderr, "Check failed at %s:%d\n", file, line);
    abort();
  }
}
#define CHECK(condition) lesson_check((condition), __FILE__, __LINE__)

int main(void) {
  /* Transfer a small pipe payload */
  {
    int fds[2];
    CHECK(pipe(fds) == 0);
    CHECK(write(fds[1], "abc", 3) == 3);
    CHECK(close(fds[1]) == 0);
    char out[4] = {0};
    CHECK(read(fds[0], out, 3) == 3 && strcmp(out, "abc") == 0);
    CHECK(close(fds[0]) == 0);
  }

  /* Observe EOF after closure */
  {
    int fds[2];
    CHECK(pipe(fds) == 0);
    CHECK(close(fds[1]) == 0);
    char byte = 0;
    CHECK(read(fds[0], &byte, 1) == 0);
    CHECK(close(fds[0]) == 0);
  }

  /* Read a payload in two pieces */
  {
    int fds[2];
    CHECK(pipe(fds) == 0);
    CHECK(write(fds[1], "abcd", 4) == 4);
    CHECK(close(fds[1]) == 0);
    char a[3] = {0}, b[3] = {0};
    CHECK(read(fds[0], a, 2) == 2 && read(fds[0], b, 2) == 2);
    CHECK(strcmp(a, "ab") == 0 && strcmp(b, "cd") == 0);
    CHECK(close(fds[0]) == 0);
  }

  /* Retain binary zeros */
  {
    int fds[2];
    unsigned char data[] = {1, 0, 2}, out[3] = {0};
    CHECK(pipe(fds) == 0);
    CHECK(write(fds[1], data, 3) == 3);
    CHECK(close(fds[1]) == 0);
    CHECK(read(fds[0], out, 3) == 3 && memcmp(data, out, 3) == 0);
    CHECK(close(fds[0]) == 0);
  }

  /* Account for duplicated ownership */
  {
    int fds[2];
    CHECK(pipe(fds) == 0);
    int duplicate = dup(fds[1]);
    CHECK(duplicate >= 0);
    CHECK(close(fds[1]) == 0 && close(duplicate) == 0);
    char byte = 0;
    CHECK(read(fds[0], &byte, 1) == 0);
    CHECK(close(fds[0]) == 0);
  }

  /* Transfer a bounded record decoder */
  {
    int fds[2];
    CHECK(pipe(fds) == 0);
    CHECK(write(fds[1], "OK7", 3) == 3);
    CHECK(close(fds[1]) == 0);
    char tag[3] = {0}, value = 0;
    CHECK(read(fds[0], tag, 2) == 2 && read(fds[0], &value, 1) == 1);
    CHECK(strcmp(tag, "OK") == 0 && value == '7');
    CHECK(close(fds[0]) == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
