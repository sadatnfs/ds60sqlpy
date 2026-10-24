#include <stdio.h>

int main(void) {
  /* Exercise 1: Use named fields
     Construct Point with x 2 and y 3.
     Expected: The field sum is 5. */

  /* Exercise 2: Copy scalar fields
     Copy a Point and change the copied x.
     Expected: The original x stays 2. */

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
