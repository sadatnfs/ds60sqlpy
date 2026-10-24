#include <stdio.h>

int main(void) {
  /* Exercise 1: Append two fragments
     Append red then space sky.
     Expected: The result is red sky with length 7. */

  /* Exercise 2: Append empty text
     Append an empty fragment to abc.
     Expected: Length and content remain unchanged. */

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
