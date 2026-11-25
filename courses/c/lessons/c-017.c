#include <stdio.h>

int main(void) {
  /* Exercise 1: Create an owned string: predict an edited check
     In worked example 1, change `CHECK(text_create(&t, "alpha"));` to
     `CHECK(text_create(&t, "alpha!"));`. Predict whether the CHECK still holds
     and why, then run and restore. Expected: `Check failed`:
     `CHECK(text_create(&t, "alpha!"));` is false, although length is 5 and
     content is alpha. */

  /* Exercise 2: Clone independent storage: debug a regression
     Worked example 2 now has a line reading `b.data[1] = 'b';`. Repair it so
     that the original remains cat again. Expected: `Check failed` at
     `strcmp(a.data, "cat") == 0 && strcmp(b.data, "bat") == 0` until the line
     reads `b.data[0] = 'b';` again. */

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
