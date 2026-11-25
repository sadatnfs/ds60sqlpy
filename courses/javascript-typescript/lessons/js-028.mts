// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Find a shortest unweighted path: change one input
// Rebuild Example A from memory, keeping the check `assert.deepEqual(shortestPath(graph,
// 'A', 'D'), ['A', 'B', 'D'])`, then propose one input change that should make it fail.
// Expected: The rebuild reproduces: A,B,D under the stated neighbor order. Your proposed
// change makes `assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D'])` fail.

// Exercise 2: Beat greedy coin selection: diagnose an edited check
// Example B's check was edited to read `assert.equal(minCoins([1, 3, 4], 1), 0);`. Run it,
// explain the failure and restore the original.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(minCoins([1, 3, 4], 1), 0);`. Restoring `assert.equal(minCoins([1, 3, 4],
// 0), 0);` brings back: two coins; amount zero needs zero coins.

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
