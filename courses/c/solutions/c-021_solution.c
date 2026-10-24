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

struct Node {
  int value;
  struct Node *next;
};
static bool push_front(struct Node **head, int value) {
  struct Node *node = malloc(sizeof *node);
  if (node == NULL)
    return false;
  node->value = value;
  node->next = *head;
  *head = node;
  return true;
}
static size_t list_length(const struct Node *head) {
  size_t n = 0;
  for (const struct Node *p = head; p != NULL; p = p->next)
    n++;
  return n;
}
static void destroy_list(struct Node **head) {
  struct Node *p = *head;
  while (p != NULL) {
    struct Node *next = p->next;
    free(p);
    p = next;
  }
  *head = NULL;
}
static void reverse_list(struct Node **head) {
  struct Node *previous = NULL, *current = *head;
  while (current != NULL) {
    struct Node *next = current->next;
    current->next = previous;
    previous = current;
    current = next;
  }
  *head = previous;
}

int main(void) {
  /* Insert at the head */
  {
    struct Node *head = NULL;
    CHECK(push_front(&head, 1) && push_front(&head, 2));
    CHECK(head->value == 2 && head->next->value == 1);
    destroy_list(&head);
  }

  /* Count a constructed list */
  {
    struct Node *head = NULL;
    for (int i = 0; i < 3; i++)
      CHECK(push_front(&head, i));
    CHECK(list_length(head) == 3);
    destroy_list(&head);
  }

  /* Handle an empty list */
  {
    struct Node *head = NULL;
    CHECK(list_length(head) == 0);
    destroy_list(&head);
    CHECK(head == NULL);
  }

  /* Reverse without reallocating */
  {
    struct Node *head = NULL;
    CHECK(push_front(&head, 1) && push_front(&head, 2) && push_front(&head, 3));
    reverse_list(&head);
    CHECK(head->value == 1 && head->next->value == 2 &&
          head->next->next->value == 3);
    destroy_list(&head);
  }

  /* Reverse a singleton */
  {
    struct Node *head = NULL;
    CHECK(push_front(&head, 7));
    reverse_list(&head);
    CHECK(head->value == 7 && head->next == NULL);
    destroy_list(&head);
  }

  /* Transfer double-reversal reasoning */
  {
    struct Node *head = NULL;
    CHECK(push_front(&head, 1) && push_front(&head, 2));
    reverse_list(&head);
    reverse_list(&head);
    CHECK(head->value == 2 && head->next->value == 1);
    destroy_list(&head);
  }
  puts("All lesson checks passed.");
  return 0;
}
