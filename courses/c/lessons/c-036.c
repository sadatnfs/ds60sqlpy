#include <stdio.h>

int main(void) {
  /* Exercise 1: Join one calculation: change one input
     Copy worked example 1, the "join one calculation" case, into a scratch pad
     and change `struct Work work = {.input = 7, .output = 0};` to `struct Work
     work = {.input = 8, .output = 0};`. Before running, predict which CHECK
     fails and which value it sees in place of the worked result (the retained
     result is 49); then run it and restore the original line. Expected: With
     `struct Work work = {.input = 8, .output = 0};` the run stops with `Check
     failed` at the CHECK on `work.output == 49`, because the "join one
     calculation" case no longer shows that the retained result is 49. Restoring
     `struct Work work = {.input = 7, .output = 0};` brings that observation
     back. */

  /* Exercise 2: Keep separate arguments: debug a regression
     A regression changed one token in worked example 2, the "keep separate
     arguments" case, so one line now reads `struct Work work[2] = {{3, 0}, {3,
     0}};`. Run the example with that line, use the failing CHECK to find why
     their independent outputs are 4 and 9 no longer holds and repair the line
     without changing the CHECK. Expected: Before the repair the run stops with
     `Check failed` at the CHECK on `work[0].output == 4 && work[1].output ==
     9`. Once the line reads `struct Work work[2] = {{2, 0}, {3, 0}};` again,
     the "keep separate arguments" case again shows that their independent
     outputs are 4 and 9. */

  /* Exercise 3: Retrieve a stable pointer result
     Have the worker return its caller-owned argument pointer.
     Expected: Join returns that same live object address. */

  /* Exercise 4: Handle a zero input
     Run the worker on input zero.
     Expected: The output is zero. */

  /* Exercise 5: Aggregate after all joins
     Run four workers for inputs 1 through 4 and sum results afterward.
     Expected: The total is 30. */

  /* Exercise 6: Transfer reusable execution
     Run the same argument object through two joined invocations sequentially.
     Expected: The second input produces its own output 16. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
