// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Find a shortest unweighted path
// Search a graph with two equal-length routes from A to D.
// Expected: A,B,D under the stated neighbor order.

// Exercise 2: Beat greedy coin selection
// Use denominations 1,3,4 to make amount 6.
// Expected: two coins; amount zero needs zero coins.

// Exercise 3: Terminate on a cyclic graph
// Search A to C through A-B-A cycles and check source-to-source.
// Expected: A,B,C and A.

// Exercise 4: Separate disconnection from malformed input
// Search a disconnected target, then supply a missing neighbor.
// Expected: undefined for no path; RangeError for invalid graph.

// Exercise 5: Represent unreachable coin amounts
// Use denomination 2 for targets 3 and 4.
// Expected: undefined and 2.

// Exercise 6: Reject invalid recurrence configurations
// Try zero, negative and fractional coins plus target 1001.
// Expected: RangeError for all invalid configurations; empty denominations cannot make 1.

console.log("Implement the six exercises in your saved copy.");
