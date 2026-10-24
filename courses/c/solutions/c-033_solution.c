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

struct Packet {
  size_t length;
  unsigned char data[];
};
static struct Packet *packet_create(const unsigned char *data, size_t length) {
  if (length > SIZE_MAX - sizeof(struct Packet) || (length > 0 && data == NULL))
    return NULL;
  struct Packet *p = malloc(sizeof *p + length);
  if (p == NULL)
    return NULL;
  p->length = length;
  if (length > 0)
    memcpy(p->data, data, length);
  return p;
}

int main(void) {
  /* Create a trailing payload */
  {
    unsigned char data[] = {1, 2, 3};
    struct Packet *p = packet_create(data, 3);
    CHECK(p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3);
    free(p);
  }

  /* Create an empty packet */
  {
    struct Packet *p = packet_create(NULL, 0);
    CHECK(p != NULL && p->length == 0);
    free(p);
  }

  /* Reject total-size overflow */
  {
    CHECK(packet_create(NULL, SIZE_MAX) == NULL);
  }

  /* Clone the complete record */
  {
    unsigned char data[] = {4, 5};
    struct Packet *a = packet_create(data, 2), *b = packet_create(data, 2);
    CHECK(a != NULL && b != NULL);
    b->data[0] = 9;
    CHECK(a->data[0] == 4 && b->data[0] == 9);
    free(a);
    free(b);
  }

  /* Preserve binary zero */
  {
    unsigned char data[] = {7, 0, 8};
    struct Packet *p = packet_create(data, 3);
    CHECK(p != NULL && p->length == 3 && p->data[1] == 0);
    free(p);
  }

  /* Transfer source independence */
  {
    unsigned char data[] = {1};
    struct Packet *p = packet_create(data, 1);
    CHECK(p != NULL);
    data[0] = 9;
    CHECK(p->data[0] == 1);
    free(p);
  }
  puts("All lesson checks passed.");
  return 0;
}
