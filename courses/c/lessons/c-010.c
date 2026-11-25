#include <stdio.h>

int main(void) {
  /* Exercise 1: Use named fields: change one input
     In worked example 1, change `struct Point p = {.x = 2, .y = 3};` to `struct
     Point p = {.x = 3, .y = 3};`. Predict which value the CHECK on `p.x + p.y
     == 5` sees, then run and restore. Expected: `Check failed` at `p.x + p.y ==
     5`; restoring `struct Point p = {.x = 2, .y = 3};` passes again. */

  /* Exercise 2: Copy scalar fields: debug a regression
     Worked example 2 now has a line reading `struct Point a = {3, 3};`. Repair
     it so that the original x stays 2 again. Expected: `Check failed` at `a.x
     == 2 && b.x == 9` until the line reads `struct Point a = {2, 3};` again. */

  /* Exercise 3: Interpret an integer alternative
     Create a tagged number with an integer payload.
     Expected: The checked payload is 7. */

  /* Exercise 4: Interpret a text alternative
     Create a tagged value containing a borrowed string.
     Expected: The text is ready. */

  /* Exercise 5: Compare semantic fields
     Compare two equal Points by x and y.
     Expected: Semantic equality is true. */

  /* Exercise 6: Transfer invalid-tag diagnosis
     Pass an unexpected discriminator to a validator.
     Expected: The validator rejects it. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
