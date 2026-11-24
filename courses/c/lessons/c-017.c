#include <stdio.h>

int main(void) {
  /* Exercise 1: Create an owned string: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(text_create(&t,
     "alpha"));` to `CHECK(text_create(&t, "alpha!"));` inside its CHECK. Before
     running, predict whether the CHECK still holds and explain why; then
     restore it. Expected: With `CHECK(text_create(&t, "alpha!"));` the run
     stops with `Check failed` at the CHECK on `t.len == 5 && strcmp(t.data,
     "alpha") == 0`, because the "create an owned string" case no longer shows
     that length is 5 and content is alpha. Restoring `CHECK(text_create(&t,
     "alpha"));` brings that observation back. */

  /* Exercise 2: Clone independent storage: debug a regression
     A regression changed one token in worked example 2, the "clone independent
     storage" case, so one line now reads `b.data[1] = 'b';`. Run the example
     with that line, use the failing CHECK to find why the original remains cat
     no longer holds and repair the line without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `strcmp(a.data, "cat") == 0 && strcmp(b.data, "bat") == 0`. Once the line
     reads `b.data[0] = 'b';` again, the "clone independent storage" case again
     shows that the original remains cat. */

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
