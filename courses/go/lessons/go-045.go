package main

import "fmt"

func main() {
	// Exercise 1: Acquire an empty lease: predict an edited check: Copy worked example 1 into a scratch pad and change `check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` to `check(acquire(&l, "a", 11, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `acquire` because the edited check no longer holds. Restoring the original line brings back the worked observation: holder becomes a and expiry 15.

	// Exercise 2: Reject a competing candidate: debug a regression: A regression changed one token in worked example 2, so one line now reads `l := Lease{Holder: "a!", Expires: 15}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `contender`; after it the line reads `l := Lease{Holder: "a", Expires: 15}` again and the request fails and a remains holder.

	// Exercise 3: Renew current leadership: Let a renew its lease before expiry.
	// Expected: Expiry advances to 18.

	// Exercise 4: Take over after expiry: Let b acquire at the exact expiry boundary.
	// Expected: Holder becomes b.

	// Exercise 5: Reject a stale fenced operation: Compare an old authority token 4 with current token 5.
	// Expected: Only token 5 is accepted by the destination model.

	// Exercise 6: Transfer invalid-duration refusal: Attempt a lease with a nonpositive duration.
	// Expected: No lease is acquired.

	fmt.Println("Implement the six investigations in your saved pad.")
}
