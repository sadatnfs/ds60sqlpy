// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Handle and decode a successful request
// Send 2 and 3 through the handler, JSON round-trip its reply, then decode it.
// Expected: status 200 and decoded total 5.

// Exercise 2: Return a stable invalid-input envelope
// Submit a string operand instead of a number.
// Expected: status 400 with bad_request and matching request id.

// Exercise 3: Distinguish route and method failures
// Use an unknown path and an unsupported method.
// Expected: 404 not_found versus 405 method_not_allowed.

// Exercise 4: Reject version or status/body disagreement
// Decode an unsupported version and a success envelope paired with status 400.
// Expected: TypeError for both malformed replies.

// Exercise 5: Require success narrowing in checked client code
// Attempt data access before checking ok in an uncalled function.
// Expected: expected compiler error; correctly narrowed success remains usable.

// Exercise 6: Keep invalid payload details out of response errors
// Include a secret-looking extra field in an invalid request.
// Expected: bad_request response does not echo the supplied value.

console.log("Implement the six exercises in your saved copy.");
