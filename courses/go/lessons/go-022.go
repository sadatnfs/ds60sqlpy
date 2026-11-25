package main

import "fmt"

func main() {
	// Exercise 1: Serve a health request: change one input: Copy worked example 1, change `health(r, httptest.NewRequest("GET", "/health", nil))` to `health(r, httptest.NewRequest("GET!", "/health", nil))` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `health` because `r.Code == 200 && r.Body.String() == "ok\n"` no longer holds.

	// Exercise 2: Reject an unsupported method: debug a regression: A one-token regression in worked example 2 makes a line read `health(r, httptest.NewRequest("POST", "/health!", nil))`. Repair it without changing the check.
	// Expected: The defective run panics with `method`; after restoring `health(r, httptest.NewRequest("POST", "/health", nil))`, the status is 405 and Allow is GET.

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
