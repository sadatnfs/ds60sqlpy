#include <stdio.h>

int main(void) {
  /* Exercise 1: Read through a const view: change one input
     Copy worked example 1, the "read through a const view" case, into a scratch
     pad and change `int value = 4;` to `int value = 5;`. Before running,
     predict which CHECK fails and which value it sees in place of the worked
     result (the read yields 4); then run it and restore the original line.
     Expected: With `int value = 5;` the run stops with `Check failed` at the
     CHECK on `*view == 4`, because the "read through a const view" case no
     longer shows that the read yields 4. Restoring `int value = 4;` brings that
     observation back. */

  /* Exercise 2: Observe another valid mutation: debug a regression
     A regression changed one token in worked example 2, the "observe another
     valid mutation" case, so one line now reads `value = 8;`. Run the example
     with that line, use the failing CHECK to find why the const view now reads
     7 no longer holds and repair the line without changing the CHECK. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on `*view
     == 7`. Once the line reads `value = 7;` again, the "observe another valid
     mutation" case again shows that the const view now reads 7. */

  /* Exercise 3: Use a fixed pointer target
     Create an int pointer that cannot be reassigned, then update its target.
     Expected: The target becomes 8. */

  /* Exercise 4: Read an immutable object
     Declare a const integer and access it through a const pointer.
     Expected: The value is 9. */

  /* Exercise 5: Pass a read-only array contract
     Sum a const array using a const pointer parameter.
     Expected: The sum is 6. */

  /* Exercise 6: Transfer snapshot independence
     Copy the scalar observed through a const view and then mutate the original.
     Expected: The snapshot remains 2 while the view reads 5. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
