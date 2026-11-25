#include <stdio.h>

int main(void) {
  /* Exercise 1: Push into an empty vector: predict an edited check
     In worked example 1, change `CHECK(vector_push(&v, 3) && vector_push(&v,
     5));` to `CHECK(vector_push(&v, 4) && vector_push(&v, 5));`. Predict
     whether the CHECK still holds and why, then run and restore. Expected:
     `Check failed`: `CHECK(vector_push(&v, 4) && vector_push(&v, 5));` is
     false, although length is 2 and values are retained. */

  /* Exercise 2: Reserve without adding elements: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(v.cap > 8 && v.len == 0);`.
     Explain why it fails although capacity is at least eight while length stays
     zero, then restore it. Expected: `Check failed` until the CHECK reads
     `CHECK(v.cap >= 8 && v.len == 0);` again, though capacity is at least eight
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
