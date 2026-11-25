package main

import "fmt"

func main() {
	// Exercise 1: Acquire an empty lease: predict an edited check: Copy worked example 1, change `check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` to `check(acquire(&l, "a", 11, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `acquire` even though `acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15` still holds.

	// Exercise 2: Reject a competing candidate: debug a regression: A one-token regression in worked example 2 makes a line read `l := Lease{Holder: "a!", Expires: 15}`. Repair it without changing the check.
	// Expected: The defective run panics with `contender`; after restoring `l := Lease{Holder: "a", Expires: 15}`, the request fails and a remains holder.

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
