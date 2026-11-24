#include <stdio.h>

int main(void) {
  /* Exercise 1: Push into an empty vector: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(vector_push(&v,
     3) && vector_push(&v, 5));` to `CHECK(vector_push(&v, 4) && vector_push(&v,
     5));` inside its CHECK. Before running, predict whether the CHECK still
     holds and explain why; then restore it. Expected: With
     `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` the run stops with
     `Check failed` at the CHECK on `v.len == 2 && v.data[0] == 3 && v.data[1]
     == 5`, because the "push into an empty vector" case no longer shows that
     length is 2 and values are retained. Restoring `CHECK(vector_push(&v, 3) &&
     vector_push(&v, 5));` brings that observation back. */

  /* Exercise 2: Reserve without adding elements: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "reserve without
     adding elements" case, so that it reads `CHECK(v.cap > 8 && v.len == 0);`.
     Run the example with that line, explain why the edited CHECK now fails even
     though the program state still means capacity is at least eight while
     length stays zero, and restore it. Expected: Before the repair the run
     stops with `Check failed` at the CHECK on `v.cap >= 8 && v.len == 0`. Once
     the line reads `CHECK(v.cap >= 8 && v.len == 0);` again, the "reserve
     without adding elements" case again shows that capacity is at least eight
     while length stays zero. */

  /* Exercise 3: Grow while preserving contents
     Push twenty sequential values.
     Expected: Every stored value matches its index. */

  /* Exercise 4: Pop from a nonempty vector
     Push 7 then pop it.
     Expected: The returned value is 7 and length becomes zero. */

  /* Exercise 5: Reject an empty pop
     Pop an empty vector with an existing output value.
     Expected: The operation fails and output stays 9. */

  /* Exercise 6: Transfer reserve failure atomicity
     Reject SIZE_MAX capacity after storing one item.
     Expected: The original value and length remain intact. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
