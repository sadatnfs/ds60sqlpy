#include <stdio.h>

int main(void) {
  /* Exercise 1: Use named fields: change one input
     Copy worked example 1, the "use named fields" case, into a scratch pad and
     change `struct Point p = {.x = 2, .y = 3};` to `struct Point p = {.x = 3,
     .y = 3};`. Before running, predict which CHECK fails and which value it
     sees in place of the worked result (the field sum is 5); then run it and
     restore the original line. Expected: With `struct Point p = {.x = 3, .y =
     3};` the run stops with `Check failed` at the CHECK on `p.x + p.y == 5`,
     because the "use named fields" case no longer shows that the field sum
     is 5. Restoring `struct Point p = {.x = 2, .y = 3};` brings that
     observation back. */

  /* Exercise 2: Copy scalar fields: debug a regression
     A regression changed one token in worked example 2, the "copy scalar
     fields" case, so one line now reads `struct Point a = {3, 3};`. Run the
     example with that line, use the failing CHECK to find why the original x
     stays 2 no longer holds and repair the line without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `a.x == 2 && b.x == 9`. Once the line reads `struct Point a = {2, 3};`
     again, the "copy scalar fields" case again shows that the original x
     stays 2. */

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
