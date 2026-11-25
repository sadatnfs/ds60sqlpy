#include <stdio.h>

int main(void) {
  /* Exercise 1: Exercise successful allocation: predict an edited check
     In worked example 1, change `CHECK(copy_with_allocator("abc", &out,
     controlled_alloc));` to `CHECK(copy_with_allocator("abc!", &out,
     controlled_alloc));`. Predict whether the CHECK still holds and why, then
     run and restore. Expected: `Check failed`:
     `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` is false,
     although the output owns an equal string. */

  /* Exercise 2: Inject allocation failure: debug a regression
     In worked example 2, `fail_allocation = true;` now reads `fail_allocation =
     false;`. Repair it so that the copy fails and output remains NULL again.
     Expected: `Check failed` at `!copy_with_allocator("abc", &out,
     controlled_alloc)` until the line reads `fail_allocation = true;` again. */

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
