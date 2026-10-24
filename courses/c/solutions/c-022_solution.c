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

enum { QUEUE_CAPACITY = 4 };
struct Queue {
  int data[QUEUE_CAPACITY];
  size_t head, count;
};
static bool enqueue(struct Queue *q, int value) {
  if (q->count == QUEUE_CAPACITY)
    return false;
  size_t index = (q->head + q->count) % QUEUE_CAPACITY;
  q->data[index] = value;
  q->count++;
  return true;
}
static bool dequeue(struct Queue *q, int *out) {
  if (q->count == 0 || out == NULL)
    return false;
  *out = q->data[q->head];
  q->head = (q->head + 1) % QUEUE_CAPACITY;
  q->count--;
  return true;
}

int main(void) {
  /* Preserve FIFO order */
  {
    struct Queue q = {0};
    int out = 0;
    CHECK(enqueue(&q, 2) && enqueue(&q, 5));
    CHECK(dequeue(&q, &out) && out == 2);
    CHECK(dequeue(&q, &out) && out == 5);
  }

  /* Reject an empty read */
  {
    struct Queue q = {0};
    int out = 9;
    CHECK(!dequeue(&q, &out) && out == 9 && q.count == 0);
  }

  /* Reject a full write */
  {
    struct Queue q = {0};
    for (int i = 0; i < 4; i++)
      CHECK(enqueue(&q, i));
    CHECK(!enqueue(&q, 99) && q.count == 4);
  }

  /* Wrap reused storage */
  {
    struct Queue q = {0};
    int out = 0;
    for (int i = 0; i < 4; i++)
      CHECK(enqueue(&q, i));
    CHECK(dequeue(&q, &out) && dequeue(&q, &out));
    CHECK(enqueue(&q, 4) && enqueue(&q, 5));
    for (int i = 2; i < 6; i++) {
      CHECK(dequeue(&q, &out) && out == i);
    }
  }

  /* Retain a real zero */
  {
    struct Queue q = {0};
    int out = 9;
    CHECK(enqueue(&q, 0) && dequeue(&q, &out) && out == 0);
  }

  /* Transfer stack contrast */
  {
    int stack[4];
    size_t length = 0;
    stack[length++] = 2;
    stack[length++] = 5;
    int out = stack[--length];
    CHECK(out == 5 && length == 1);
  }
  puts("All lesson checks passed.");
  return 0;
}
