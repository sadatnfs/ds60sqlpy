#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
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

struct Publication {
  atomic_bool ready;
  int value;
};
static void *atomic_publisher(void *argument) {
  struct Publication *p = argument;
  p->value = 42;
  atomic_store_explicit(&p->ready, true, memory_order_release);
  return NULL;
}

int main(void) {
  /* Inspect fetch-add semantics */
  {
    atomic_int value;
    atomic_init(&value, 2);
    int old = atomic_fetch_add(&value, 3);
    CHECK(old == 2 && atomic_load(&value) == 5);
  }

  /* Compare and exchange successfully */
  {
    atomic_int value;
    atomic_init(&value, 2);
    int expected = 2;
    CHECK(atomic_compare_exchange_strong(&value, &expected, 7));
    CHECK(atomic_load(&value) == 7);
  }

  /* Inspect failed compare-exchange */
  {
    atomic_int value;
    atomic_init(&value, 3);
    int expected = 2;
    CHECK(!atomic_compare_exchange_strong(&value, &expected, 7));
    CHECK(expected == 3 && atomic_load(&value) == 3);
  }

  /* Count independent events */
  {
    atomic_int count;
    atomic_init(&count, 0);
    for (int i = 0; i < 10; i++)
      atomic_fetch_add_explicit(&count, 1, memory_order_relaxed);
    CHECK(atomic_load_explicit(&count, memory_order_relaxed) == 10);
  }

  /* Publish initialized data */
  {
    struct Publication p;
    atomic_init(&p.ready, false);
    p.value = 0;
    pthread_t worker;
    CHECK(pthread_create(&worker, NULL, atomic_publisher, &p) == 0);
    while (!atomic_load_explicit(&p.ready, memory_order_acquire)) {
      sched_yield();
    }
    CHECK(p.value == 42);
    CHECK(pthread_join(worker, NULL) == 0);
  }

  /* Transfer an atomic exchange */
  {
    atomic_bool ready;
    atomic_init(&ready, false);
    bool old = atomic_exchange(&ready, true);
    CHECK(!old && atomic_load(&ready));
  }
  puts("All lesson checks passed.");
  return 0;
}
