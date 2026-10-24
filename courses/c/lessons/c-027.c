#include <stdio.h>

int main(void) {
  /* Exercise 1: Exercise successful allocation
     Copy a tiny string using the working allocator.
     Expected: The output owns an equal string. */

  /* Exercise 2: Inject allocation failure
     Configure the allocator to return NULL.
     Expected: The copy fails and output remains NULL. */

  /* Exercise 3: Preserve an existing output pointer
     Fail allocation while output points to a separate valid buffer.
     Expected: The output pointer remains unchanged. */

  /* Exercise 4: Test an empty valid input
     Copy empty text through the working allocator.
     Expected: A valid empty owned string is returned. */

  /* Exercise 5: Retain a normal case after failure
     Run one failing call followed by a successful call.
     Expected: The later call succeeds independently. */

  /* Exercise 6: Transfer a distinguishing content check
     Copy case-sensitive text and compare exact content.
     Expected: Red remains different from red. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
