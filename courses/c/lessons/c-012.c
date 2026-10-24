#include <stdio.h>

int main(void) {
  /* Exercise 1: Read through a const view
     Observe a mutable integer through const int pointer.
     Expected: The read yields 4. */

  /* Exercise 2: Observe another valid mutation
     Change the mutable object through its original name.
     Expected: The const view now reads 7. */

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
