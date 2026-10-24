#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert and retrieve
     Store key 1 with value 7.
     Expected: Lookup succeeds with 7. */

  /* Exercise 2: Resolve a collision
     Insert keys 1 and 9, which share the initial slot.
     Expected: Both values remain retrievable. */

  /* Exercise 3: Replace an existing key
     Write key 2 twice with different values.
     Expected: The latest value is 8. */

  /* Exercise 4: Distinguish absent from zero
     Store key zero with value zero and query a missing key.
     Expected: The stored zero succeeds; the missing key fails. */

  /* Exercise 5: Reject a full-table insertion
     Fill all eight slots and insert a new ninth key.
     Expected: The operation returns false without looping forever. */

  /* Exercise 6: Transfer replacement while full
     Replace an existing key after filling the table.
     Expected: Replacement still succeeds. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
