#include <stdio.h>

int main(void) {
  /* Exercise 1: Push into an empty vector
     Push 3 and 5 into a zero-initialized vector.
     Expected: Length is 2 and values are retained. */

  /* Exercise 2: Reserve without adding elements
     Reserve capacity eight.
     Expected: Capacity is at least eight while length stays zero. */

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
