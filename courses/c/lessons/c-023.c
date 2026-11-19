#include <stdio.h>

int main(void) {
  /* Exercise 1: Insert and retrieve: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(table_put(&t, 1,
     7) && table_get(&t, 1, &out) && out == 7);` to `CHECK(table_put(&t, 2, 7)
     && table_get(&t, 1, &out) && out == 7);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: The changed run stops with `Check failed` at the CHECK on
     `table_put(&t, 1, 7) && table_get(&t, 1, &out) && out == 7`. Restoring the
     original line brings back the worked observation: lookup succeeds with 7.
   */

  /* Exercise 2: Resolve a collision: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(table_put(&t, 1, 10) && table_put(&t, 10, 90));`. Run worked example
     2 with that line, explain why the edited CHECK now fails for the same
     program state, and restore it. Expected: Before the repair the run stops
     with `Check failed` at the CHECK on `table_get(&t, 9, &out) && out == 90`;
     after it the line reads `CHECK(table_put(&t, 1, 10) && table_put(&t, 9,
     90));` again and both values remain retrievable. */

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
