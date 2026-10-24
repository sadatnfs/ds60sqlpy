#include <stdio.h>

int main(void) {
  /* Exercise 1: Copy a representation safely
     Copy a float into bytes and back into a float object.
     Expected: The restored value is 1.5. */

  /* Exercise 2: Inspect bytes without type punning
     Read an integer representation through unsigned char.
     Expected: The byte view has exactly sizeof(int) bytes. */

  /* Exercise 3: Handle overlapping moves
     Shift abc right by one within a buffer using memmove.
     Expected: The buffer prefix becomes aabc. */

  /* Exercise 4: Keep typed access in a real object
     Copy an int value into another int with memcpy.
     Expected: The target value becomes 9. */

  /* Exercise 5: Inspect an alignment requirement
     Read the alignment of int and max_align_t.
     Expected: Both requirements are positive. */

  /* Exercise 6: Transfer a bounded byte copy
     Copy a four-byte payload into an equally sized destination.
     Expected: All bytes match exactly. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
