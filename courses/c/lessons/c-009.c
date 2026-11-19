#include <stdio.h>

int main(void) {
  /* Exercise 1: Relate indexing and arithmetic: change one input
     Copy worked example 1 into a scratch pad and change `int values[] = {2, 4,
     6};` to `int values[] = {2, 5, 6};`. Before running, predict which CHECK
     fails and which value it now sees; then run it and restore the original
     line. Expected: The changed run stops with `Check failed` at the CHECK on
     `values[1] == *(values + 1) && *(values + 1) == 4`. Restoring the original
     line brings back the worked observation: both yield 4. */

  /* Exercise 2: Measure an array interval: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `int *end = values - 3;`. Run worked example 2 with that line, use the
     failing CHECK to locate the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `n == 3`; after it the line reads `int *end = values + 3;` again
     and the difference is 3 elements. */

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
