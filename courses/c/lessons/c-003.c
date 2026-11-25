#include <stdio.h>

int main(void) {
  /* Exercise 1: Group before calculating: predict an edited check
     In worked example 1, change `CHECK((2 + 3) * 4 == 20);` to `CHECK((3 + 3) *
     4 == 20);`. Predict whether the CHECK still holds and why, then run and
     restore. Expected: `Check failed`: `CHECK((3 + 3) * 4 == 20);` is false,
     although the values are 14 and 20. */

  /* Exercise 2: Use a short-circuit guard: debug a regression
     Worked example 2 now has a line reading `bool found = length >= 0 &&
     values[0] == 7;`. Repair it so that the access is skipped and the condition
     is false again. Expected: `Check failed` at `!found` until the line reads
     `bool found = length > 0 && values[0] == 7;` again. */

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
