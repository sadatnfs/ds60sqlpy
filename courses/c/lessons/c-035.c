#include <stdio.h>

int main(void) {
  /* Exercise 1: Install and restore a handler: predict an edited check
     In worked example 1, change `CHECK(signal(SIGINT, previous) != SIG_ERR);`
     to `CHECK(signal(SIGINT, previous) == SIG_ERR);`. Predict whether the CHECK
     still holds and why, then run and restore. Expected: `Check failed`:
     `CHECK(signal(SIGINT, previous) == SIG_ERR);` is false, although both
     operations succeed. */

  /* Exercise 2: Record a raised notification: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(signal(SIGINT, previous) ==
     SIG_ERR);`. Explain why it fails although the signal flag becomes one, then
     restore it. Expected: `Check failed` until the CHECK reads
     `CHECK(signal(SIGINT, previous) != SIG_ERR);` again, though the signal flag
     becomes one. */

  /* Exercise 3: Keep work outside the handler
     Raise SIGINT with the lesson handler installed and let a normal-flow
     function turn the recorded flag into a shutdown decision. Expected: The
     decision is continue before the signal and stop after the handler records
     it. */

  /* Exercise 4: Handle no notification
     Install the handler without raising a signal, inspect the decision and
     restore the previous disposition. Expected: Installing a handler records no
     notification, and the restoring call returns the lesson handler. */

  /* Exercise 5: Reinstall after a delivery
     Raise SIGINT once, reinstall the handler in normal flow, then raise it a
     second time before restoring the original disposition. Expected: Both
     deliveries are handled. In the classroom worker the reinstalling call
     returns SIG_DFL, because glibc in -std=c17 mode reset the disposition after
     the first delivery. */

  /* Exercise 6: Transfer a bounded shutdown model
     Raise SIGINT while two tasks are active and stop admitting work in normal
     flow, retaining the active-work count. Expected: Admission stops and
     unfinished work remains visible. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
