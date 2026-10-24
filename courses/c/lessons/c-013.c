#include <stdio.h>

int main(void) {
  /* Exercise 1: Use a parenthesized macro safely
     Square the side-effect-free expression 2+3.
     Expected: The result is 25. */

  /* Exercise 2: Prefer a typed helper for mutation
     Pass value++ to a normal square function.
     Expected: The result is 9 and value increments once to 4. */

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
