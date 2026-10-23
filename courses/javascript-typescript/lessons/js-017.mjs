// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Request a valid local calculation
// GET /sum with a=2 and b=3 and inspect status, content type and JSON.
// Expected: status 200; application/json; total 5.

// Exercise 2: Inspect an HTTP error without expecting fetch rejection
// Request an unknown route and inspect the actual response.
// Expected: fetch resolves; status 404, ok false, error not_found.

// Exercise 3: Encode query values through the URL API
// Round-trip a query containing spaces, ampersand and equals without contacting a server.
// Expected: the value round-trips as one parameter.

// Exercise 4: Reject repeated or invalid parameters
// Request repeated a values and a non-integer b value.
// Expected: both responses are 400 with invalid_parameters.

// Exercise 5: Reject an unsupported method
// POST to the read-only sum route without a body.
// Expected: status 405 and Allow: GET.

// Exercise 6: Guard arithmetic overflow after parsing
// Add one to Number.MAX_SAFE_INTEGER through the endpoint.
// Expected: status 400 rather than a rounded success value.

console.log("Implement the six exercises in your saved copy.");
