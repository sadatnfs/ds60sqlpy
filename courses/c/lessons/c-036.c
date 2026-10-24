#include <stdio.h>

int main(void) {
  /* Exercise 1: Join one calculation
     Start a thread squaring input 7 and join it.
     Expected: The retained result is 49. */

  /* Exercise 2: Keep separate arguments
     Start two workers with inputs 2 and 3.
     Expected: Their independent outputs are 4 and 9. */

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
