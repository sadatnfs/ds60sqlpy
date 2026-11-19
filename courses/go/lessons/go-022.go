package main

import "fmt"

func main() {
	// Exercise 1: Serve a health request: change one input: Copy worked example 1 into a scratch pad and change `health(r, httptest.NewRequest("GET", "/health", nil))` to `health(r, httptest.NewRequest("GET!", "/health", nil))`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `health` because `r.Code == 200 && r.Body.String() == "ok\n"` no longer holds. Restoring the original line brings back the worked observation: the status is 200 and the body is ok plus a newline.

	// Exercise 2: Reject an unsupported method: debug a regression: A regression changed one token in worked example 2, so one line now reads `health(r, httptest.NewRequest("POST", "/health!", nil))`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `method`; after it the line reads `health(r, httptest.NewRequest("POST", "/health", nil))` again and the status is 405 and Allow is GET.

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
