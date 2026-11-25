#include <stdio.h>

int main(void) {
  /* Exercise 1: Join one calculation: change one input
     In worked example 1, change `struct Work work = {.input = 7, .output = 0};`
     to `struct Work work = {.input = 8, .output = 0};`. Predict which value the
     CHECK on `work.output == 49` sees, then run and restore. Expected: `Check
     failed` at `work.output == 49`; restoring `struct Work work = {.input = 7,
     .output = 0};` passes again. */

  /* Exercise 2: Keep separate arguments: debug a regression
     Worked example 2 now has a line reading `struct Work work[2] = {{3, 0}, {3,
     0}};`. Repair it so that their independent outputs are 4 and 9 again.
     Expected: `Check failed` at `work[0].output == 4 && work[1].output == 9`
     until the line reads `struct Work work[2] = {{2, 0}, {3, 0}};` again. */

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
