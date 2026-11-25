#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare length and storage: change one input
     In worked example 1, change `char word[] = "cat";` to `char word[] =
     "cat!";`. Predict which value the CHECK on `strlen(word) == 3 && sizeof
     word == 4` sees, then run and restore. Expected: `Check failed` at
     `strlen(word) == 3 && sizeof word == 4`; restoring `char word[] = "cat";`
     passes again. */

  /* Exercise 2: Modify owned text: debug a regression
     Worked example 2 now has a line reading `word[1] = 'b';`. Repair it so that
     the result is bat again. Expected: `Check failed` at `strcmp(word, "bat")
     == 0` until the line reads `word[0] = 'b';` again. */

  /* Exercise 3: Detect bounded truncation
     Format hello into a four-character buffer.
     Expected: The required length is 5 and stored text is hel. */

  /* Exercise 4: Accept exact capacity
     Store cat in a four-character buffer.
     Expected: The complete text fits with its terminator. */

  /* Exercise 5: Compare content rather than pointers
     Create two separate arrays containing cat.
     Expected: strcmp reports equality. */

  /* Exercise 6: Transfer an empty string
     Create a one-character array containing only zero.
     Expected: Its string length is zero. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
