#include <assert.h>
#include <limits.h>
#include <pthread.h>
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

struct CounterState {
  pthread_mutex_t mutex;
  int count, iterations;
};
static void *increment_worker(void *argument) {
  struct CounterState *s = argument;
  for (int i = 0; i < s->iterations; i++) {
    CHECK(pthread_mutex_lock(&s->mutex) == 0);
    s->count++;
    CHECK(pthread_mutex_unlock(&s->mutex) == 0);
  }
  return NULL;
}
static int locked_total(size_t workers, int iterations) {
  CHECK(workers <= 5);
  struct CounterState s = {.count = 0, .iterations = iterations};
  CHECK(pthread_mutex_init(&s.mutex, NULL) == 0);
  pthread_t threads[5];
  for (size_t i = 0; i < workers; i++)
    CHECK(pthread_create(&threads[i], NULL, increment_worker, &s) == 0);
  for (size_t i = 0; i < workers; i++)
    CHECK(pthread_join(threads[i], NULL) == 0);
  int result = s.count;
  CHECK(pthread_mutex_destroy(&s.mutex) == 0);
  return result;
}
struct ReadyState {
  pthread_mutex_t mutex;
  pthread_cond_t condition;
  bool ready;
  int value;
};
static void *publish_worker(void *argument) {
  struct ReadyState *s = argument;
  CHECK(pthread_mutex_lock(&s->mutex) == 0);
  s->value = 42;
  s->ready = true;
  CHECK(pthread_cond_signal(&s->condition) == 0);
  CHECK(pthread_mutex_unlock(&s->mutex) == 0);
  return NULL;
}
static int wait_for_value(void) {
  struct ReadyState s = {.ready = false, .value = 0};
  CHECK(pthread_mutex_init(&s.mutex, NULL) == 0);
  CHECK(pthread_cond_init(&s.condition, NULL) == 0);
  pthread_t worker;
  CHECK(pthread_create(&worker, NULL, publish_worker, &s) == 0);
  CHECK(pthread_mutex_lock(&s.mutex) == 0);
  while (!s.ready)
    CHECK(pthread_cond_wait(&s.condition, &s.mutex) == 0);
  int result = s.value;
  CHECK(pthread_mutex_unlock(&s.mutex) == 0);
  CHECK(pthread_join(worker, NULL) == 0);
  CHECK(pthread_cond_destroy(&s.condition) == 0);
  CHECK(pthread_mutex_destroy(&s.mutex) == 0);
  return result;
}

int main(void) {
  /* Protect a shared count */
  {
    CHECK(locked_total(4, 100) == 400);
  }

  /* Handle one worker */
  {
    CHECK(locked_total(1, 7) == 7);
  }

  /* Handle zero loop iterations */
  {
    CHECK(locked_total(2, 0) == 0);
  }

  /* Wait for a predicate */
  {
    CHECK(wait_for_value() == 42);
  }

  /* Repeat independent synchronization */
  {
    CHECK(wait_for_value() == 42 && wait_for_value() == 42);
  }

  /* Transfer count invariance */
  {
    CHECK(locked_total(2, 5) == 10 && locked_total(5, 2) == 10);
  }
  puts("All lesson checks passed.");
  return 0;
}
