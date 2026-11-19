#include <stdio.h>

int main(void) {
  /* Exercise 1: Use a parenthesized macro safely: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(SQUARE(2 + 3) ==
     25);` to `CHECK(SQUARE(3 + 3) == 25);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: The changed run stops with `Check failed` at the CHECK on
     `SQUARE(2 + 3) == 25`. Restoring the original line brings back the worked
     observation: the result is 25. */

  /* Exercise 2: Prefer a typed helper for mutation: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int value = 4;`. Run worked example 2 with that line, use the failing
     CHECK to locate the defect and repair it without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `result == 9 && value == 4`; after it the line reads `int value = 3;`
     again and the result is 9 and value increments once to 4. */

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
