# js-028: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Types clarify an algorithm's interface, but correctness depends on its invariant. Breadth-first search explores a graph in layers of edge distance. Marking a vertex when enqueuing it ensures the vertex enters the queue once, even when edges form cycles. A parent map records each first-discovery edge, allowing the shortest unweighted path to be reconstructed from target to source.

Adjacency-list BFS performs \(O(V+E)\) work under ordinary Map lookup assumptions and stores O(V) extra state. An array plus a cursor avoids repeated shift operations that move remaining elements. Several shortest paths may exist; neighbor order defines this implementation's deterministic tie policy. Weighted edges need another algorithm, such as Dijkstra for nonnegative weights. BFS does not minimize arbitrary travel cost merely because its path has few edges.

Dynamic programming reuses overlapping subproblem results. For minimum coin count, best[a] is the smallest number of allowed coins summing to amount a. best[0]=0. Each other state minimizes best[a-coin]+1 over usable denominations. Infinity represents an unreachable amount. The recurrence assumes unbounded reuse of positive integer coins. For coins 1,3,4 and target 6, greedy selection gives 4+1+1, while the recurrence discovers 3+3. The table has O(amount) memory and O(amount times number-of-coins) work, so numeric magnitude is part of its cost.

**Breadth-first search:** Layered exploration finding fewest-edge paths in an unweighted graph.

**Parent map:** First-discovery predecessors used to reconstruct a path.

**Dynamic programming:** Reusing results of overlapping subproblems.

**Recurrence:** A rule computing a state from smaller solved states.

## Reading the implementation

ReadonlyMap<string, readonly string[]> states that search consumes the graph without modifying it. Runtime checks require every referenced neighbor to exist. A null parent marks the source; an absent Map entry means undiscovered. Reconstruction follows parent links until null. The DP table is filled in increasing amount order so every dependency is already available. Positive integer denominations and a target cap preserve this dependency order and bound resource use.

## Exercise 1: Find a shortest unweighted path: change one input

Task: Close Example A and rebuild it in a fresh `main.mts`, keeping the check `assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D'])`. Then propose one input change that would make that check fail and explain why before trying it.

Both two-edge routes are shortest. The implementation chooses the first discovered route rather than claiming the answer is mathematically unique.

The unchanged code is the exercise block of Example A:

```typescript
const graph: Graph = new Map([
  ['A', ['B', 'C']],
  ['B', ['D']],
  ['C', ['D']],
  ['D', []],
]);
assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D']);
```

**Expected:** Your rebuild reproduces the worked observation (A,B,D under the stated neighbor order), and your proposed change makes the check `assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D'])` fail.

**Verify:** Run the rebuild first and confirm the `{"checks":1,"status":"passed"}` receipt, then the changed copy. Name the value that makes `assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D'])` fail in the changed copy.

## Exercise 2: Beat greedy coin selection: diagnose an edited check

Task: A careless edit changed a check in Example B so that it reads `assert.equal(minCoins([1, 3, 4], 1), 0);`. Run Example B with that line, explain why the edited check now fails for the same program state, and restore it.

The recurrence evaluates every possible final coin. It avoids the attractive local choice of 4 that leads to a worse total count.

The unchanged code is the exercise block of Example B:

```typescript
assert.equal(minCoins([1, 3, 4], 6), 2);
assert.equal(minCoins([1, 3, 4], 0), 0);
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.equal(minCoins([1, 3, 4], 0), 0)`; after it the line reads `assert.equal(minCoins([1, 3, 4], 0), 0);` again and two coins; amount zero needs zero coins.

**Verify:** Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that `assert.equal(minCoins([1, 3, 4], 0), 0)` accepts.

## Exercise 3: Terminate on a cyclic graph

Task: Search A to C through A-B-A cycles and check source-to-source.

Marking on enqueue prevents repeated insertion through the cycle. The source begins discovered at distance zero.

```typescript
const graph: Graph = new Map([
  ['A', ['B']],
  ['B', ['A', 'C']],
  ['C', ['B']],
]);
assert.deepEqual(shortestPath(graph, 'A', 'C'), ['A', 'B', 'C']);
assert.deepEqual(shortestPath(graph, 'A', 'A'), ['A']);
```

**Expected:** A,B,C and A.

**Verify:** Keep a check equivalent to `assert.deepEqual(shortestPath(graph, 'A', 'A'), ['A'])` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## Exercise 4: Separate disconnection from malformed input

Task: Search a disconnected target, then supply a missing neighbor.

No path is a valid answer for a well-formed graph. Missing vertices violate the input contract and are rejected even if source equals target.

```typescript
assert.equal(
  shortestPath(
    new Map([
      ['A', []],
      ['B', []],
    ]),
    'A',
    'B',
  ),
  undefined,
);
assert.throws(() => shortestPath(new Map([['A', ['missing']]]), 'A', 'A'), RangeError);
```

**Expected:** undefined for no path; RangeError for invalid graph.

**Verify:** Keep a check equivalent to `assert.throws(() => shortestPath(new Map([['A', ['missing']]]), 'A', 'A'), RangeError)` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## Exercise 5: Represent unreachable coin amounts

Task: Use denomination 2 for targets 3 and 4.

Infinity remains an internal unreachable sentinel. The public return type exposes absence instead of pretending Infinity is a valid count.

```typescript
assert.equal(minCoins([2], 3), undefined);
assert.equal(minCoins([2], 4), 2);
```

**Expected:** undefined and 2.

**Verify:** Keep a check equivalent to `assert.equal(minCoins([2], 4), 2)`. As a control, change `assert.equal(minCoins([2], 4), 2);` to `assert.equal(minCoins([3], 4), 2);` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Reject invalid recurrence configurations

Task: Try zero, negative and fractional coins plus target 1001.

Positive coins guarantee dependencies point to smaller amounts. A target bound prevents unexpectedly large allocations in this small teaching implementation.

```typescript
for (const coins of [[0], [-1], [1.5]]) assert.throws(() => minCoins(coins, 5), RangeError);
assert.throws(() => minCoins([1], 1001), RangeError);
assert.equal(minCoins([], 1), undefined);
```

**Expected:** RangeError for all invalid configurations; empty denominations cannot make 1.

**Verify:** Keep a check equivalent to `assert.throws(() => minCoins(coins, 5), RangeError)`. As a control, change `for (const coins of [[0], [-1], [1.5]]) assert.throws(() => minCoins(coins, 5), RangeError);` to `for (const coins of [[1], [-1], [1.5]]) assert.throws(() => minCoins(coins, 5), RangeError);`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
