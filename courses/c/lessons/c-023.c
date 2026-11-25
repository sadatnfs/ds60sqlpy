#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert and retrieve: predict an edited check
     In worked example 1, change `CHECK(table_put(&t, 1, 7) && table_get(&t, 1,
     &out) && out == 7);` to `CHECK(table_put(&t, 2, 7) && table_get(&t, 1,
     &out) && out == 7);`. Predict whether the CHECK still holds and why, then
     run and restore. Expected: `Check failed`: `CHECK(table_put(&t, 2, 7) &&
     table_get(&t, 1, &out) && out == 7);` is false, although lookup succeeds
     with 7. */

  /* Exercise 2: Resolve a collision: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(table_put(&t, 1, 10) &&
     table_put(&t, 10, 90));`. Explain why it fails although both values remain
     retrievable, then restore it. Expected: `Check failed` until the CHECK
     reads `CHECK(table_put(&t, 1, 10) && table_put(&t, 9, 90));` again, though
     both values remain retrievable. */

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
