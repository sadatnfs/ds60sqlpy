#include <stdio.h>

int main(void) {
  /* Exercise 1: Install and restore a handler: predict an edited check
     Copy worked example 1 into a scratch pad and change `CHECK(signal(SIGINT,
     previous) != SIG_ERR);` to `CHECK(signal(SIGINT, previous) == SIG_ERR);`
     inside its CHECK. Before running, predict whether the CHECK still holds and
     explain why; then restore it. Expected: With `CHECK(signal(SIGINT,
     previous) == SIG_ERR);` the run stops with `Check failed` at the CHECK on
     `signal(SIGINT, previous) != SIG_ERR`, because the "install and restore a
     handler" case no longer shows that both operations succeed. Restoring
     `CHECK(signal(SIGINT, previous) != SIG_ERR);` brings that observation back.
   */

  /* Exercise 2: Record a raised notification: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "record a raised
     notification" case, so that it reads `CHECK(signal(SIGINT, previous) ==
     SIG_ERR);`. Run the example with that line, explain why the edited CHECK
     now fails even though the program state still means the signal flag becomes
     one, and restore it. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `signal(SIGINT, previous) != SIG_ERR`. Once the
     line reads `CHECK(signal(SIGINT, previous) != SIG_ERR);` again, the "record
     a raised notification" case again shows that the signal flag becomes one.
   */

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
