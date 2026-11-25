#include <stdio.h>

int main(void) {
  /* Exercise 1: Use a parenthesized macro safely: predict an edited check
     In worked example 1, change `CHECK(SQUARE(2 + 3) == 25);` to
     `CHECK(SQUARE(3 + 3) == 25);`. Predict whether the CHECK still holds and
     why, then run and restore. Expected: `Check failed`: `CHECK(SQUARE(3 + 3)
     == 25);` is false, although the result is 25. */

  /* Exercise 2: Prefer a typed helper for mutation: debug a regression
     Worked example 2 now has a line reading `int value = 4;`. Repair it so that
     the result is 9 and value increments once to 4 again. Expected: `Check
     failed` at `result == 9 && value == 4` until the line reads `int value =
     3;` again. */

  /* Exercise 3: Require a representation fact
     Check the language-required char size at translation time.
     Expected: Compilation accepts the true static assertion. */

  /* Exercise 4: Read a configuration constant
     Use a fixed capacity macro of 8.
     Expected: The declared buffer has eight elements. */

  /* Exercise 5: Select by a simple type
     Use a generic selection for int and double expressions.
     Expected: The selected labels are integer and floating. */

  /* Exercise 6: Transfer an inline-style function contract
     Square zero and negative three through the typed helper.
     Expected: The results are 0 and 9. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
