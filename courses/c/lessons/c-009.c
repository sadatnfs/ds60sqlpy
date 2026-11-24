#include <stdio.h>

int main(void) {
  /* Exercise 1: Relate indexing and arithmetic: change one input
     Copy worked example 1, the "relate indexing and arithmetic" case, into a
     scratch pad and change `int values[] = {2, 4, 6};` to `int values[] = {2,
     5, 6};`. Before running, predict which CHECK fails and which value it sees
     in place of the worked result (both yield 4); then run it and restore the
     original line. Expected: With `int values[] = {2, 5, 6};` the run stops
     with `Check failed` at the CHECK on `values[1] == *(values + 1) && *(values
     + 1) == 4`, because the "relate indexing and arithmetic" case no longer
     shows that both yield 4. Restoring `int values[] = {2, 4, 6};` brings that
     observation back. */

  /* Exercise 2: Measure an array interval: debug a regression
     A regression changed one token in worked example 2, the "measure an array
     interval" case, so one line now reads `int *end = values - 3;`. Run the
     example with that line, use the failing CHECK to find why the difference is
     3 elements no longer holds and repair the line without changing the CHECK.
     Expected: Before the repair the run stops with `Check failed` at the CHECK
     on `n == 3`. Once the line reads `int *end = values + 3;` again, the
     "measure an array interval" case again shows that the difference is 3
     elements. */

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
