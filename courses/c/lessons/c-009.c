#include <stdio.h>

int main(void) {
  /* Exercise 1: Relate indexing and arithmetic
     Read the second element through both forms.
     Expected: Both yield 4. */

  /* Exercise 2: Measure an array interval
     Subtract begin from one-past end.
     Expected: The difference is 3 elements. */

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
