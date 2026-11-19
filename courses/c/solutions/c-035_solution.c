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
static bool stop_requested(void) { return signal_seen != 0; }

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
    signal_seen = 0;
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    CHECK(!stop_requested());
    CHECK(raise(SIGINT) == 0);
    CHECK(stop_requested());
    CHECK(signal(SIGINT, previous) != SIG_ERR);
    signal_seen = 0;
  }

  /* Handle no notification */
  {
    signal_seen = 0;
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    CHECK(!stop_requested());
    CHECK(signal(SIGINT, previous) == lesson_handler);
  }

  /* Reinstall after a delivery */
  {
    signal_seen = 0;
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    CHECK(raise(SIGINT) == 0 && signal_seen == 1);
    void (*after)(int) = signal(SIGINT, lesson_handler);
    CHECK(after == SIG_DFL || after == lesson_handler);
    signal_seen = 0;
    CHECK(raise(SIGINT) == 0 && signal_seen == 1);
    CHECK(signal(SIGINT, previous) != SIG_ERR);
    signal_seen = 0;
  }

  /* Transfer a bounded shutdown model */
  {
    signal_seen = 0;
    void (*previous)(int) = signal(SIGINT, lesson_handler);
    CHECK(previous != SIG_ERR);
    bool accepting = true;
    int active = 2;
    CHECK(raise(SIGINT) == 0);
    if (stop_requested())
      accepting = false;
    CHECK(!accepting && active == 2);
    CHECK(signal(SIGINT, previous) != SIG_ERR);
    signal_seen = 0;
  }
  puts("All lesson checks passed.");
  return 0;
}
