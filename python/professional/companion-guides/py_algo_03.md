# Graph Traversal, Priority Queues, and Shortest-Path Evidence

**Stable ID:** `python-algo-03`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-algo-02`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Open the [learner script](../lessons/py_algo_03.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_algo_03.py
```

Dependencies: Python standard library. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_algo_03_solutions.md) and [runnable reference](../solutions/py_algo_03_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Graph:** A set of vertices and edges describing permitted relationships or transitions; this lesson uses directed weighted edges.

- **Frontier:** The discovered vertices or candidate states waiting to be processed by a traversal.

- **Priority queue:** A structure that removes the item with smallest priority efficiently; a heap implements this without fully sorting all items.

- **Relaxation:** Replacing a best-known path cost when a newly considered edge produces a cheaper route.

The frontier data structure determines which search question an algorithm answers. A FIFO queue explores vertices by number of edges from the start, so breadth-first search finds minimum-hop paths in an unweighted graph. A priority queue explores the smallest known cumulative cost, which is needed when edge weights differ. A one-edge route can be much more expensive than a two-edge route.

Dijkstra's algorithm maintains best-known distances and repeatedly removes the lowest-cost frontier entry. With nonnegative edge weights, a removed best distance cannot later be improved by traveling through a more expensive unexplored state. Negative edges break that argument. The lesson rejects them rather than silently running an algorithm whose proof no longer applies.

Python's heapq has no direct decrease-key operation. A simple implementation pushes a new entry when a better route is discovered and leaves the older entry in the heap. On removal, compare its recorded cost with the current best distance and skip it if stale. This can create several heap entries for one vertex, but the distance table remains the source of truth.

A parent map records the predecessor used by each improving path. Reconstructing a route is a separate operation: walk backward from goal to start, detect malformed cycles or unknown parent labels, then reverse the sequence. An unreachable vertex should have infinite distance and no route, not a fabricated empty successful path. A start-to-itself route legitimately has zero cost and contains the start vertex.

Topological ordering solves another graph problem: order every vertex before its outgoing neighbors in an acyclic graph. Kahn's algorithm removes zero-indegree vertices and decreases their neighbors' indegrees. If fewer than all vertices can be removed, a cycle remains. A heap can choose the lexicographically smallest available label for deterministic output, adding a tie policy without changing dependency correctness.

The final exercise uses the same heap mechanism to keep the largest k stream values. A size-k min-heap stores current candidates, with its smallest value at the root. New larger values can replace that root. This bounds candidate memory by k, unlike sorting every input. The lesson compares numeric results, actual routes and cycle failures so an algorithm's name is never treated as evidence of correctness.

## Worked examples and syntax anatomy

### Example 1

```python
graph = {"a": [("b", 10.0), ("c", 1.0)], "b": [], "c": [("b", 1.0)]}
assert len(["a", "b"]) - 1 == 1
assert len(["a", "c", "b"]) - 1 == 2
direct_cost = graph["a"][0][1]
via_c_cost = graph["a"][1][1] + graph["c"][0][1]
assert via_c_cost == 2.0 < direct_cost == 10.0
print("Fewest hops differs from lowest cost:1 edge costs10;2 edges cost2")
```

Breadth-first search would discover b directly in one hop. A cost-aware search must also consider the two-edge route through c, whose total weight is two. The fixture is a counterexample to using hop count as a proxy for weighted travel cost.

### Example 2

```python
heap = []
for value in [4.0, 1.0, 9.0, 3.0, 8.0]:
    if len(heap) < 3:
        heapq.heappush(heap, value)
    else:
        heapq.heappushpop(heap, value)
assert sorted(heap, reverse=True) == [9.0, 8.0, 4.0]
assert heap[0] == 4.0
print("Largest three:", sorted(heap, reverse=True))
```

The heap array is not a fully sorted list. Its root is only guaranteed to be the smallest retained candidate. Sorting the final small heap creates the desired presentation order while avoiding a full sort of all input values.

## Exercises

1. **Validate the shortest-path assumptions.** Require string vertex labels, edges to existing vertices and finite nonnegative numeric weights. Reject Boolean weights, missing neighbor vertices, negative weights and nonfinite weights with ValueError. Empty graphs are valid structures.

**Expected:** a->b with weight 2 passes when both vertices exist. Weight-1, NaN, True or an edge to absent z fails.

2. **Find minimum edge counts.** Return minimum hop counts from start to reachable vertices using a deque frontier. Ignore edge magnitudes for this hop-count question, but validate graph and require start to exist. Do not include unreachable vertices in the result.

**Expected:** For a->b(weight 10), a->c(weight 1), c->b(weight 1), hops are a 0, b1, c1. An isolated d is absent; an unknown start raises ValueError.

3. **Use cumulative cost and skip stale entries.** Return distances and parent links for every graph vertex using a min-heap and nonnegative weights. Unreachable vertices retain infinity and None. Push improved candidates and skip stale popped entries. Reject an absent start or cumulative-cost overflow.

**Expected:** In the a, b, c, d fixture, distances are a 0, c1, b2, d infinity and parent[b]=c. The earlier direct b cost 10 must not overwrite the improved cost 2.

4. **Verify a route rather than only its score.** Reconstruct a start-to-goal path from parent links. Return None for an unreachable goal, return [start] when start equals goal, and reject absent vertices, unknown parent labels or a cycle encountered during reconstruction.

**Expected:** Parents from dijkstra produce[a, c, b] for a to b and None for a to d. A parent cycle x->y->x raises ValueError rather than looping.

5. **Order dependencies and expose cycles.** Return a topological order using indegrees and a heap of available string labels, choosing the lexicographically smallest available vertex. Include isolated vertices. Raise ValueError when a directed cycle prevents processing every vertex.

**Expected:** a->c, b->c plus isolated d yields [a, b, c, d]. Every edge source precedes its target. a->b, b->a raises ValueError; empty graph returns [].

6. **Transfer priority-queue reasoning to a stream.** Consume finite numeric values and retain the k largest values, including duplicates, using at most k heap entries. Return descending values. Require nonnegative non-Boolean integer k and reject nonfinite input; k0 still validates the input stream.

**Expected:** [4,1,9,3,8] with k3 gives [9,8,4]; [2,2,1] with k2 gives [2,2]. Empty input or k0 yields []; NaN raises ValueError.

## Common mistakes and diagnosis

If a weighted route has too high a cost, check whether a FIFO queue was used where a priority queue was required. If stale routes overwrite better distances, compare each popped cost with the current distance table. If reconstruction loops, validate parent-chain identities and cycles. If a dependency ordering omits nodes, compare processed count with the full vertex set, including isolated nodes. If a heap printout looks unsorted, inspect the root invariant rather than assuming the entire internal list is ordered. Never claim Dijkstra supports negative weights just because one small negative-edge fixture happened to return a plausible path.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [Python heapq priority queues](https://docs.python.org/3/library/heapq.html).

- [Python deque](https://docs.python.org/3/library/collections.html#collections.deque).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-03: Graph Traversal, Priority Queues, and Shortest-Path Evidence.
Read python/professional/companion-guides/py_algo_03.md and python/professional/lessons/py_algo_03.py. Direct prerequisites: python-algo-02.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
