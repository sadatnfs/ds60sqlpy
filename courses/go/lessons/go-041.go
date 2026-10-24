package main

import "fmt"

func main() {
	// Exercise 1: Accept explicit secure configuration: Validate an HTTPS endpoint, lesson namespace and explicit context name.
	// Expected: The configuration is accepted.

	// Exercise 2: Reject insecure transport: Validate an HTTP endpoint.
	// Expected: The configuration is rejected.

	// Exercise 3: Reject ambient context selection: Omit the context name.
	// Expected: Validation rejects the configuration.

	// Exercise 4: Constrain a namespace: Attempt a namespace containing a slash.
	// Expected: Validation rejects it.

	// Exercise 5: Construct a bounded request: Build an HTTPS list request with a live context without sending it.
	// Expected: The method and URL path are correct.

	// Exercise 6: Transfer userinfo rejection: Reject an endpoint embedding userinfo.
	// Expected: The embedded credential form is rejected.

	fmt.Println("Implement the six investigations in your saved pad.")
}
