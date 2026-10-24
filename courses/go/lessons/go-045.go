package main

import "fmt"

func main() {
	// Exercise 1: Acquire an empty lease: Let candidate a acquire at logical time 10 for five units.
	// Expected: Holder becomes a and expiry 15.

	// Exercise 2: Reject a competing candidate: Let b request an unexpired lease held by a.
	// Expected: The request fails and a remains holder.

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
