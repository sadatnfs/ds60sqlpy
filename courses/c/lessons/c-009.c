#include <stdio.h>

int main(void) {
  /* Exercise 1: Relate indexing and arithmetic: change one input
     In worked example 1, change `int values[] = {2, 4, 6};` to `int values[] =
     {2, 5, 6};`. Predict which value the CHECK on `values[1] == *(values + 1)
     && *(values + 1) == 4` sees, then run and restore. Expected: `Check failed`
     at `values[1] == *(values + 1) && *(values + 1) == 4`; restoring `int
     values[] = {2, 4, 6};` passes again. */

  /* Exercise 2: Measure an array interval: debug a regression
     Worked example 2 now has a line reading `int *end = values - 3;`. Repair it
     so that the difference is 3 elements again. Expected: `Check failed` at `n
     == 3` until the line reads `int *end = values + 3;` again. */

  /* Exercise 3: Traverse before the boundary
     Sum through a begin/end pointer loop.
     Expected: The result is 12. */

  /* Exercise 4: Construct a subview
     View two elements starting at the second element.
     Expected: The subview contains 4 and 6. */

  /* Exercise 5: Keep an empty boundary non-dereferenced
     Use equal begin and end pointers inside one array.
     Expected: The traversal performs zero accesses. */

  /* Exercise 6: Transfer mutation through a subview
     Change the first element of a borrowed suffix.
     Expected: The corresponding original element changes. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
