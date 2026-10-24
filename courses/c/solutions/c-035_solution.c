#include <assert.h>
#include <limits.h>
#include <signal.h>
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

static volatile sig_atomic_t signal_seen = 0;
static void lesson_handler(int number) {
  if (number == SIGINT)
    signal_seen = 1;
}

int main(void) {
  /* Install and restore a handler */
  {
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    CHECK(signal(SIGINT, previous) != SIG_ERR);
  }

  /* Record a raised notification */
  {
    signal_seen = 0;
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    CHECK(raise(SIGINT) == 0);
    CHECK(signal_seen == 1);
    CHECK(signal(SIGINT, previous) != SIG_ERR);
  }

  /* Keep work outside the handler */
  {
    signal_seen = 1;
    bool stop = (signal_seen != 0);
    CHECK(stop);
    signal_seen = 0;
  }

  /* Handle no notification */
  {
    signal_seen = 0;
    CHECK(signal_seen == 0);
  }

  /* Reset between independent operations */
  {
    signal_seen = 1;
    signal_seen = 0;
    CHECK(signal_seen == 0);
  }

  /* Transfer a bounded shutdown model */
  {
    bool accepting = true;
    int active = 2;
    signal_seen = 1;
    if (signal_seen)
      accepting = false;
    CHECK(!accepting && active == 2);
    signal_seen = 0;
  }
  puts("All lesson checks passed.");
  return 0;
}
