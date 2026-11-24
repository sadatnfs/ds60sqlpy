#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert at the head: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(push_front(&head, 1) && push_front(&head, 2));` to
     `CHECK(push_front(&head, 2) && push_front(&head, 2));` inside its CHECK.
     Before running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: With `CHECK(push_front(&head, 2) && push_front(&head,
     2));` the run stops with `Check failed` at the CHECK on `head->value == 2
     && head->next->value == 1`, because the "insert at the head" case no longer
     shows that the list order is 2 then 1. Restoring `CHECK(push_front(&head,
     1) && push_front(&head, 2));` brings that observation back. */

  /* Exercise 2: Count a constructed list: debug a regression
     A regression changed one token in worked example 2, the "count a
     constructed list" case, so one line now reads `for (int i = 0; i <= 3;
     i++)`. Run the example with that line, use the failing CHECK to find why
     the length is 3 no longer holds and repair the line without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `list_length(head) == 3`. Once the line reads `for (int i = 0; i <
     3; i++)` again, the "count a constructed list" case again shows that the
     length is 3. */

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
