#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert at the head: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(push_front(&head, 1) && push_front(&head, 2));` to
     `CHECK(push_front(&head, 2) && push_front(&head, 2));` inside its CHECK.
     Before running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: The changed run stops with `Check failed` at the
     CHECK on `head->value == 2 && head->next->value == 1`. Restoring the
     original line brings back the worked observation: the list order is 2 then
     1. */

  /* Exercise 2: Count a constructed list: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `for (int i = 0; i <= 3; i++)`. Run worked example 2 with that line, use
     the failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `list_length(head) == 3`; after it the line reads `for (int i = 0;
     i < 3; i++)` again and the length is 3. */

  /* Exercise 3: Handle an empty list
     Measure and destroy a null head.
     Expected: Length is zero and head stays NULL. */

  /* Exercise 4: Reverse without reallocating
     Build 3, 2, 1 and reverse it.
     Expected: The order becomes 1, 2, 3. */

  /* Exercise 5: Reverse a singleton
     Reverse a one-node list.
     Expected: Its value and terminating link are preserved. */

  /* Exercise 6: Transfer double-reversal reasoning
     Reverse a two-node list twice.
     Expected: Its original order is restored. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
