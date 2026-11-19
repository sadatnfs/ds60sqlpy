// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Find a shortest unweighted path: change one input
// Close Example A and rebuild it in a fresh `main.mts`, keeping the check
// `assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D'])`. Then propose one input
// change that would make that check fail and explain why before trying it.
// Expected: Your rebuild reproduces the worked observation (A,B,D under the stated neighbor
// order), and your proposed change makes the check `assert.deepEqual(shortestPath(graph,
// 'A', 'D'), ['A', 'B', 'D'])` fail.

// Exercise 2: Beat greedy coin selection: diagnose an edited check
// A careless edit changed a check in Example B so that it reads `assert.equal(minCoins([1,
// 3, 4], 1), 0);`. Run Example B with that line, explain why the edited check now fails for
// the same program state, and restore it.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(minCoins([1, 3, 4], 0), 0)`; after it the line reads
// `assert.equal(minCoins([1, 3, 4], 0), 0);` again and two coins; amount zero needs zero
// coins.

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
