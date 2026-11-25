#include <stdio.h>

int main(void) {
  /* Exercise 1: Append two fragments: predict an edited check
     In worked example 1, change `CHECK(append_text(&b, "red") &&
     append_text(&b, " sky"));` to `CHECK(append_text(&b, "red!") &&
     append_text(&b, " sky"));`. Predict whether the CHECK still holds and why,
     then run and restore. Expected: `Check failed`: `CHECK(append_text(&b,
     "red!") && append_text(&b, " sky"));` is false, although the result is red
     sky with length 7. */

  /* Exercise 2: Append empty text: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(append_text(&b, "abc!") &&
     append_text(&b, ""));`. Explain why it fails although length and content
     remain unchanged, then restore it. Expected: `Check failed` until the CHECK
     reads `CHECK(append_text(&b, "abc") && append_text(&b, ""));` again, though
     length and content remain unchanged. */

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
