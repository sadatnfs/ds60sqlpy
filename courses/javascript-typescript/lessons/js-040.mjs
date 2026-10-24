// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Create and retrieve an item over real HTTP
// POST item A with value 2, then GET the list.
// Expected: 201 created; subsequent 200 list contains exactly A.

// Exercise 2: Reject malformed data before changing state
// Send malformed JSON and a wrong-shaped object, then inspect the repository through GET.
// Expected: both 400; list remains empty.

// Exercise 3: Preserve original state on duplicate creation
// Create A with value 2, then try A with value 9.
// Expected: second request 409; stored value remains 2.

// Exercise 4: Enforce body and media-type contracts
// Send 513 body bytes, then a text/plain payload.
// Expected: 413 for size and 415 for media type.

// Exercise 5: Distinguish unknown routes and unsupported methods
// Request an absent path and DELETE on the item route.
// Expected: 404 and 405 respectively.

// Exercise 6: Correlate safe events and prove listener cleanup
// Request health, inspect its request id and event keys, then check the server after the
// helper exits.
// Expected: matching id and status; server no longer listening.

console.log("Implement the six exercises in your saved copy.");
