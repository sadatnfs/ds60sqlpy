// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Aggregate valid rows through a real child process
// Send two rows worth 250 and 300 cents to the CLI.
// Expected: exit 0; stdout is exactly one JSON result with 2 rows and 550 cents; stderr empty.

// Exercise 2: Reject unknown arguments before consuming data
// Invoke the tool with --unknown.
// Expected: exit 2; stdout empty; stderr includes usage.

// Exercise 3: Report the first invalid row without a partial result
// Send a valid first row and malformed JSON on line 2.
// Expected: exit 2; stdout empty; stderr identifies line 2.

// Exercise 4: Reject duplicate business identifiers
// Send two valid rows with the same id.
// Expected: exit 2 with duplicate id diagnostic.

// Exercise 5: Define empty input deliberately
// Send whitespace and empty lines only.
// Expected: exit 0 with rows 0 and totalCents 0.

// Exercise 6: Enforce an input budget before retaining all data
// Send 4097 bytes to a CLI whose cap is 4096.
// Expected: exit 2 with input limit diagnostic; stdout empty.

console.log("Implement the six exercises in your saved copy.");
