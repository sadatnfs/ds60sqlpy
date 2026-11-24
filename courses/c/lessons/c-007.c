#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare length and storage: change one input
     Copy worked example 1, the "compare length and storage" case, into a
     scratch pad and change `char word[] = "cat";` to `char word[] = "cat!";`.
     Before running, predict which CHECK fails and which value it sees in place
     of the worked result (strlen is 3 while array size is 4); then run it and
     restore the original line. Expected: With `char word[] = "cat!";` the run
     stops with `Check failed` at the CHECK on `strlen(word) == 3 && sizeof word
     == 4`, because the "compare length and storage" case no longer shows that
     strlen is 3 while array size is 4. Restoring `char word[] = "cat";` brings
     that observation back. */

  /* Exercise 2: Modify owned text: debug a regression
     A regression changed one token in worked example 2, the "modify owned text"
     case, so one line now reads `word[1] = 'b';`. Run the example with that
     line, use the failing CHECK to find why the result is bat no longer holds
     and repair the line without changing the CHECK. Expected: Before the repair
     the run stops with `Check failed` at the CHECK on `strcmp(word, "bat") ==
     0`. Once the line reads `word[0] = 'b';` again, the "modify owned text"
     case again shows that the result is bat. */

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
