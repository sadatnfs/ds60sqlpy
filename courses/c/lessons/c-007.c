#include <stdio.h>

int main(void) {
  /* Exercise 1: Compare length and storage: change one input
     Copy worked example 1 into a scratch pad and change `char word[] = "cat";`
     to `char word[] = "cat!";`. Before running, predict which CHECK fails and
     which value it now sees; then run it and restore the original line.
     Expected: The changed run stops with `Check failed` at the CHECK on
     `strlen(word) == 3 && sizeof word == 4`. Restoring the original line brings
     back the worked observation: strlen is 3 while array size is 4. */

  /* Exercise 2: Modify owned text: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `word[1] = 'b';`. Run worked example 2 with that line, use the failing
     CHECK to locate the defect and repair it without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `strcmp(word, "bat") == 0`; after it the line reads `word[0] = 'b';`
     again and the result is bat. */

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
