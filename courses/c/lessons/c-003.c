#include <stdio.h>

int main(void) {
  /* Exercise 1: Group before calculating
     Compare 2+3*4 with (2+3)*4.
     Expected: The values are 14 and 20. */

  /* Exercise 2: Use a short-circuit guard
     Guard an array access with a false length test.
     Expected: The access is skipped and the condition is false. */

  /* Exercise 3: Sequence updates explicitly
     Increment x and then calculate twice its updated value.
     Expected: x is 2 and the result is 4. */

  /* Exercise 4: Expose signed-unsigned conversion
     Compare -1 with 1U under the usual conversion rules.
     Expected: The comparison -1 < 1U is false on this int/unsigned-int pair. */

  /* Exercise 5: Choose one conditional branch
     Select a valid value while the other branch would divide by zero.
     Expected: Only the chosen branch is evaluated and result is 7. */

  /* Exercise 6: Transfer assignment diagnosis
     Assign 3 to a variable, then separately compare it with 3.
     Expected: The assignment changes the variable and equality tests it. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
