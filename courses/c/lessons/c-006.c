#include <stdio.h>

int main(void) {
  /* Exercise 1: Derive a local element count
     Create a three-element array and calculate its count with sizeof.
     Expected: The count is 3. */

  /* Exercise 2: Pass an explicit length
     Sum three elements through a pointer-and-length API.
     Expected: The result is 12. */

  /* Exercise 3: Inspect partial initialization
     Initialize only the first element of a three-element array.
     Expected: The remaining two elements are zero. */

  /* Exercise 4: Use a logical prefix
     Sum only the first two elements of a three-element array.
     Expected: The result is 6. */

  /* Exercise 5: Handle an empty logical view
     Call the sum contract with null and length zero.
     Expected: The sum is zero and no access occurs. */

  /* Exercise 6: Transfer independent array storage
     Copy elements into a distinct array and mutate the copy.
     Expected: The original first element remains 1. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
