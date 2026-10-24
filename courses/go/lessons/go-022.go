package main

import "fmt"

func main() {
	// Exercise 1: Serve a health request: Send GET /health to the handler.
	// Expected: The status is 200 and the body is ok plus a newline.

	// Exercise 2: Reject an unsupported method: Send POST /health.
	// Expected: The status is 405 and Allow is GET.

	// Exercise 3: Reject an unknown route: Send GET /missing.
	// Expected: The status is 404.

	// Exercise 4: Check content metadata: Inspect the successful response content type.
	// Expected: The response declares text/plain with UTF-8.

	// Exercise 5: Repeat without shared mutation: Run two independent health requests.
	// Expected: Both responses succeed identically.

	// Exercise 6: Transfer query independence: Call /health with an unrelated query parameter.
	// Expected: The path still matches and returns 200.

	fmt.Println("Implement the six investigations in your saved pad.")
}
