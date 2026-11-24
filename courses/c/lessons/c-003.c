#include <stdio.h>

int main(void) {
  /* Exercise 1: Group before calculating: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK((2 + 3) * 4 ==
     20);` to `CHECK((3 + 3) * 4 == 20);` inside its CHECK. Before running,
     predict whether the CHECK still holds and explain why; then restore it.
     Expected: With `CHECK((3 + 3) * 4 == 20);` the run stops with `Check
     failed` at the CHECK on `(2 + 3) * 4 == 20`, because the "group before
     calculating" case no longer shows that the values are 14 and 20. Restoring
     `CHECK((2 + 3) * 4 == 20);` brings that observation back. */

  /* Exercise 2: Use a short-circuit guard: debug a regression
     A regression changed one token in worked example 2, the "use a
     short-circuit guard" case, so one line now reads `bool found = length >= 0
     && values[0] == 7;`. Run the example with that line, use the failing CHECK
     to find why the access is skipped and the condition is false no longer
     holds and repair the line without changing the CHECK. Expected: Before the
     repair the run stops with `Check failed` at the CHECK on `!found`. Once the
     line reads `bool found = length > 0 && values[0] == 7;` again, the "use a
     short-circuit guard" case again shows that the access is skipped and the
     condition is false. */

  /* Exercise 3: Sequence updates explicitly
     Increment x and then calculate twice its updated value.
     Expected: x is 2 and the result is 4. */

  /* Exercise 4: Expose signed-unsigned conversion
     Compare -1 with 1U under the usual conversion rules.
     Expected: The comparison -1 < 1U is false on this int/unsigned-int pair. */

  /* Exercise 5: Choose one conditional branch
     Select a valid value while the other branch would divide by zero.
     Expected: Only the chosen branch is evaluated and result is 7. */

  /* Exercise 6: Transfer integer promotion
     Add two unsigned char values 200 and 100, then store the sum back into an
     unsigned char. Expected: The promoted int sum is 300; the stored unsigned
     char is 44. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
