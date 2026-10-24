#include <stdio.h>

int main(void) {
  /* Exercise 1: Trace block shadowing
     Declare an outer value 3 and a separate inner value 7.
     Expected: After the inner block, the outer remains 3. */

  /* Exercise 2: Retain static state
     Call a function with one static counter twice.
     Expected: It returns 1 and then 2. */

  /* Exercise 3: Return a static address
     Get a pointer to a static read-only value.
     Expected: The target remains valid and equals 7. */

  /* Exercise 4: Keep automatic state per call
     Call a function with an initialized local counter twice.
     Expected: Both calls return 1. */

  /* Exercise 5: Separate visibility from lifetime
     Retain a value copy obtained from an inner block.
     Expected: The copied scalar remains 9 afterward. */

  /* Exercise 6: Transfer initialized aggregation
     Initialize an accumulator before processing an empty range.
     Expected: The result is the defined zero identity. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
