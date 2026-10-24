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

struct Work {
  int input, output;
};
static void *square_worker(void *argument) {
  struct Work *work = argument;
  work->output = work->input * work->input;
  return work;
}

int main(void) {
  /* Join one calculation */
  {
    struct Work work = {.input = 7, .output = 0};
    pthread_t thread;
    CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
    CHECK(pthread_join(thread, NULL) == 0);
    CHECK(work.output == 49);
  }

  /* Keep separate arguments */
  {
    struct Work work[2] = {{2, 0}, {3, 0}};
    pthread_t threads[2];
    for (size_t i = 0; i < 2; i++)
      CHECK(pthread_create(&threads[i], NULL, square_worker, &work[i]) == 0);
    for (size_t i = 0; i < 2; i++)
      CHECK(pthread_join(threads[i], NULL) == 0);
    CHECK(work[0].output == 4 && work[1].output == 9);
  }

  /* Retrieve a stable pointer result */
  {
    struct Work work = {5, 0};
    pthread_t thread;
    void *returned = NULL;
    CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
    CHECK(pthread_join(thread, &returned) == 0);
    CHECK(returned == &work && work.output == 25);
  }

  /* Handle a zero input */
  {
    struct Work work = {0, 9};
    pthread_t thread;
    CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
    CHECK(pthread_join(thread, NULL) == 0);
    CHECK(work.output == 0);
  }

  /* Aggregate after all joins */
  {
    struct Work work[4] = {{1, 0}, {2, 0}, {3, 0}, {4, 0}};
    pthread_t threads[4];
    for (size_t i = 0; i < 4; i++)
      CHECK(pthread_create(&threads[i], NULL, square_worker, &work[i]) == 0);
    int sum = 0;
    for (size_t i = 0; i < 4; i++) {
      CHECK(pthread_join(threads[i], NULL) == 0);
      sum += work[i].output;
    }
    CHECK(sum == 30);
  }

  /* Transfer reusable execution */
  {
    struct Work work = {3, 0};
    pthread_t thread;
    CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
    CHECK(pthread_join(thread, NULL) == 0);
    work.input = 4;
    CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
    CHECK(pthread_join(thread, NULL) == 0);
    CHECK(work.output == 16);
  }
  puts("All lesson checks passed.");
  return 0;
}
