#include <stdio.h>

int main(void) {
  /* Exercise 1: Append two fragments: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(append_text(&b,
     "red") && append_text(&b, " sky"));` to `CHECK(append_text(&b, "red!") &&
     append_text(&b, " sky"));` inside its CHECK. Before running, predict
     whether the CHECK still holds and explain why; then restore it. Expected:
     The changed run stops with `Check failed` at the CHECK on `b.len == 7 &&
     strcmp(b.data, "red sky") == 0`. Restoring the original line brings back
     the worked observation: the result is red sky with length 7. */

  /* Exercise 2: Append empty text: diagnose an edited check
     A careless edit changed the CHECK in worked example 2 so that it reads
     `CHECK(append_text(&b, "abc!") && append_text(&b, ""));`. Run worked
     example 2 with that line, explain why the edited CHECK now fails for the
     same program state, and restore it. Expected: Before the repair the run
     stops with `Check failed` at the CHECK on `b.len == 3 && strcmp(b.data,
     "abc") == 0`; after it the line reads `CHECK(append_text(&b, "abc") &&
     append_text(&b, ""));` again and length and content remain unchanged. */

  /* Exercise 3: Fill to exact payload capacity
     Append fifteen characters to capacity sixteen.
     Expected: The complete payload fits and remains terminated. */

  /* Exercise 4: Reject one extra character
     Fill the builder then append x.
     Expected: The append fails without changing prior content. */

  /* Exercise 5: Reject an oversized first fragment
     Try a fragment longer than payload capacity.
     Expected: The builder remains an empty valid string. */

  /* Exercise 6: Transfer a delimiter protocol
     Build a,b,c with explicit separators.
     Expected: The exact result is a,b,c. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
