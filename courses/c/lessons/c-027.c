#include <stdio.h>

int main(void) {
  /* Exercise 1: Exercise successful allocation: predict an edited check
     Copy worked example 1 into a scratch pad and change
     `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` to
     `CHECK(copy_with_allocator("abc!", &out, controlled_alloc));` inside its
     CHECK. Before running, predict whether the CHECK still holds and explain
     why; then restore it. Expected: With `CHECK(copy_with_allocator("abc!",
     &out, controlled_alloc));` the run stops with `Check failed` at the CHECK
     on `strcmp(out, "abc") == 0`, because the "exercise successful allocation"
     case no longer shows that the output owns an equal string. Restoring
     `CHECK(copy_with_allocator("abc", &out, controlled_alloc));` brings that
     observation back. */

  /* Exercise 2: Inject allocation failure: debug a regression
     A regression changed `fail_allocation = true;` to `fail_allocation =
     false;` in worked example 2, the "inject allocation failure" case. Run the
     example with that change, use the failing CHECK to explain why the copy
     fails and output remains NULL no longer holds and repair it without
     changing the CHECK. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `!copy_with_allocator("abc", &out,
     controlled_alloc)`. Once the line reads `fail_allocation = true;` again,
     the "inject allocation failure" case again shows that the copy fails and
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
