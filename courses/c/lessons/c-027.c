#include <stdio.h>

int main(void) {
  /* Exercise 1: Exercise successful allocation: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` to
     `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` inside its
     CHECK. Before running, predict whether the CHECK still holds and explain
     why; then restore it. Expected: The changed run stops with `Check failed`
     at the CHECK on `strcmp(out, "abc") == 0`. Restoring the original line
     brings back the worked observation: the output owns an equal string. */

  /* Exercise 2: Inject allocation failure: debug a regression
     A regression changed `fail_allocation = true;` to `fail_allocation =
     false;` in worked example 2. Run worked example 2 with that change, use the
     failing CHECK to explain the defect and repair it without changing the
     CHECK. Expected: Before the repair the run stops with `Check failed` at the
     CHECK on `!copy_with_allocator("abc", &out, controlled_alloc)`; after it
     the line reads `fail_allocation = true;` again and the copy fails and
     output remains NULL. */

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
