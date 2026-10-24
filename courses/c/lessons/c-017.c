#include <stdio.h>

int main(void) {
  /* Exercise 1: Create an owned string
     Create an owner for alpha.
     Expected: Length is 5 and content is alpha. */

  /* Exercise 2: Clone independent storage
     Clone cat and mutate the clone to bat.
     Expected: The original remains cat. */

  /* Exercise 3: Borrow without releasing
     Read through a const pointer borrowed from an owner.
     Expected: The borrowed content is ready. */

  /* Exercise 4: Represent an owned empty string
     Create an owner for empty text.
     Expected: Length is zero but a valid terminator exists. */

  /* Exercise 5: Make cleanup idempotent
     Destroy the same reset owner twice.
     Expected: The owner stays empty. */

  /* Exercise 6: Transfer a deliberate move
     Move ownership by assigning the struct and clearing the source.
     Expected: Only the destination retains the allocation. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
