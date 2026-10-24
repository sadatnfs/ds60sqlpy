#include <stdio.h>

int main(void) {
  /* Exercise 1: Parse a valid list
     Parse 1,20,3 into capacity three.
     Expected: Three values are returned in order. */

  /* Exercise 2: Reject an empty field
     Parse 1,,3.
     Expected: The parse fails and prior output is unchanged. */

  /* Exercise 3: Reject a trailing separator
     Parse 1,2,.
     Expected: The parse fails. */

  /* Exercise 4: Enforce output capacity
     Parse three values into capacity two.
     Expected: The operation fails without an overflow. */

  /* Exercise 5: Reject numeric overflow
     Parse a number with far too many digits.
     Expected: The range check rejects it. */

  /* Exercise 6: Transfer exact grammar boundaries
     Parse zero successfully and reject leading whitespace.
     Expected: Zero is valid; space-prefixed input is not. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
