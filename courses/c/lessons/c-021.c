#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert at the head: predict an edited check
     In worked example 1, change `CHECK(push_front(&head, 1) &&
     push_front(&head, 2));` to `CHECK(push_front(&head, 2) && push_front(&head,
     2));`. Predict whether the CHECK still holds and why, then run and restore.
     Expected: `Check failed`: `CHECK(push_front(&head, 2) && push_front(&head,
     2));` is false, although the list order is 2 then 1. */

  /* Exercise 2: Count a constructed list: debug a regression
     Worked example 2 now has a line reading `for (int i = 0; i <= 3; i++)`.
     Repair it so that the length is 3 again. Expected: `Check failed` at
     `list_length(head) == 3` until the line reads `for (int i = 0; i < 3; i++)`
     again. */

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
