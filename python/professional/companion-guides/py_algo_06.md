# Disjoint Sets and Minimum Spanning Forests

**Stable ID:** `python-algo-06`. Allow about 150 minutes for reading,
tracing and independent implementation. This estimate is not a deadline.

## How to run this lesson

Run `./classroom` from the repository root and choose **Python** in the shared
`/classroom` directory. Select this unit, read its Python capability notice,
and open the saved coding pad. Windows learners use the same launcher in
WSL 2. Docker supplies the prepared Python Core environment and the required
standard-library modules; no extra package, dataset or service is needed.
Paste the complete [learner script](../lessons/py_algo_06.py), save and Run.
The two worked examples print their observations. The six task functions
remain unimplemented and are not called by the opening demonstrations.

Every browser Run starts a fresh process. Include imports, fixtures and your
checks together, and save the source that reproduces an observation. The
learning volume retains code, notes and results; it does not retain live tree
objects, heap contents or generator state between processes. A successful
opening demonstration is evidence for those examples, not completion of the
six independent implementations.

An optional separately prepared contributor environment can run
`uv run --no-sync python python/professional/lessons/py_algo_06.py`
from the repository root. See [contributor setup](../../../CONTRIBUTING.md)
for that route and the [classroom guide](../../../docs/classroom-experience.md)
for browser persistence. The host checkout and interpreter do not read the
browser's Docker learning volume. All inputs in this lesson are original,
tiny offline fixtures.

## Level and prerequisites

- **Level:** Advanced Python algorithm practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-algo-02`, [stable sorting, heaps and greedy invariants](py_algo_02.md).
- **Direct prerequisite:** `python-algo-03`, [graphs, shortest paths and dynamic programming](py_algo_03.md).
- **Artifacts:** [learner](../lessons/py_algo_06.py), [explained answers](../solutions/py_algo_06_solutions.md), [executable reference](../solutions/py_algo_06_solution.py).

## Learning objectives

Maintain a partition through parent pointers, root sizes and a component
count. Explain why path compression changes representation without changing
connectivity, and apply union by size with an explicit tie rule. Use that state
to select original edge records for Kruskal's algorithm, then separate a
spanning-forest feasibility check from independent evidence of minimum cost.

## Starting point and observable outcome

This is `python-algo-06`. Its direct prerequisites are `python-algo-02` and `python-algo-03`: stable ordering, graph traversal, heaps and the distinction between hop count and path cost should already be familiar. Use the Docker classroom's prepared Python Core environment. Every example is standard-library Python with bounded offline graphs and no external graph service.

You will maintain a partition of vertices as edges are added, then use that partition to build a minimum spanning forest. The final evidence must show both structural feasibility and optimal cost on small independently checked cases. This is a different objective from the shortest-path algorithms in the prerequisite: a minimum-cost network need not contain the shortest route from a chosen origin.

## Vocabulary and concepts

- **Representative:** The root label returned for a component. It identifies
  current set membership; it is not a permanent business ID or a shortest-path
  predecessor from the original graph.
- **Path compression:** Redirecting the traversed parent links toward their
  already-established root. It shortens later searches while preserving the
  partition, root sizes and number of components.
- **Spanning forest:** An acyclic selection that connects each component of
  the original undirected graph. Spanning is a structural condition; minimum
  total weight is an additional optimization claim.

### Equivalence classes and a parent forest

A **disjoint-set structure** partitions a fixed set of labels into nonoverlapping components. Initially every vertex is its own component. A **find** operation returns the representative of a vertex's component. A **union** merges two components and reports whether membership changed. The representative is an implementation choice, not necessarily the first vertex inserted or a permanent domain identifier.

Represent components with parent pointers. A root points to itself; following any other parent chain eventually reaches a root. These parent edges form an internal forest, which is distinct from the graph edges being analyzed. A parent link does not mean the original graph contains an edge between those labels, and it cannot be used as a shortest-path route.

The provided `DisjointSet` also stores root sizes and a component count. Sizes exist only at roots and count all members in that component. After a successful union, one root disappears from the size map and the component count decreases by one. A repeated union of already connected vertices changes neither quantity.

## Syntax anatomy and ownership

The learner scaffold supplies a dataclass containing `parent`, `size` and `components`. `make_sets` builds fresh dictionaries from unique string labels. The functions mutate their own state by design, while the original vertex list and graph edge list stay unchanged. The state is inspectable for teaching, but callers must not rewrite size tables or parent links outside the declared operations.

A find operation follows a chain using an ordinary loop. The root condition is `parent[current] == current`. The implementation then visits the path again and redirects each traversed node to that root. Save the previous next pointer before overwriting a parent; otherwise you can lose the rest of the path that still needs compression.

An unknown endpoint should be rejected before union mutates either path. Detecting a broken encountered link or parent cycle also prevents an accidental infinite loop, but the fast operations are not a complete integrity repair service for arbitrary external state corruption. Their complexity claims assume API-produced state.

## Worked example: compression changes representation

Predict the parent of `c` before and after the update. This complete example starts from a small parent forest and exposes the path being shortened.

```python
parent = {"a": "a", "b": "a", "c": "b", "x": "x"}
current = "c"
path = []
while parent[current] != current:
    path.append(current)
    current = parent[current]
assert current == "a" and path == ["c", "b"]
for vertex in path:
    parent[vertex] = current
assert parent == {"a": "a", "b": "a", "c": "a", "x": "x"}
print("Compression preserves two components:", parent)
```

The component containing `a`, `b` and `c` is unchanged. Vertex `x` remains isolated. The operation made later finds cheaper by reducing indirection, but it neither added an original graph edge nor discovered a new connection. A program that treats compression as another union would incorrectly decrease the component count.

Change the original pointer for `a` to `c`. There is now no self-parented root along that chain. A correct diagnostic must stop with an error instead of running indefinitely. Changing a cycle into a tree by arbitrary pointer reassignment would invent a partition rather than validate the one supplied.

## Union by size and the cost model

When representatives differ, attach the smaller component's root under the larger component's root. If sizes tie, this unit chooses the lexicographically smaller root. Each time a node's depth increases through union by size, the size of its component at least doubles. Without compression, this bounds depth logarithmically in the number of vertices.

Path compression further shortens future searches. The familiar near-constant amortized bound applies to a sequence of disjoint-set operations, not a promise that every individual call takes exactly constant time. Sorting and reporting components have separate costs. `component_groups` visits all labels and sorts canonical tuples, so it is intentionally more expensive than checking two representatives.

Canonical groups are useful evidence because root choices can differ between valid implementations. Compare sets of members rather than relying on a particular root except where this lesson explicitly tests its tie rule. Every vertex must occur exactly once, including isolated vertices and the empty-string label if it was declared.

## Minimum spanning forests and the cut intuition

For an undirected weighted graph, a spanning tree connects every vertex of a connected component without cycles. A spanning forest contains one such tree for each component, including singleton trees with no edges. For \(n\) vertices and \(c\) connected components, its selected edge count is

\[
|F|=n-c.
\]

Kruskal's algorithm sorts candidate edges by increasing weight and accepts an edge exactly when it connects two current components. The cut property supplies the justification: a lightest edge crossing a suitable partition can be included in an optimal forest. Accepting it joins two pieces without closing a cycle, and repeated acceptance grows a minimum solution.

Negative weights are valid here. Unlike Dijkstra's nonnegative-edge precondition, Kruskal relies on sorted edge cost and cycle avoidance, not monotone shortest-path distances. A negative self-loop is still excluded because a forest cannot contain a cycle. This illustrates why copying validation rules from a neighboring graph algorithm can wrongly reject valid problems or accept the wrong objective.

Parallel edges remain distinct candidate records. The function returns original edge indices, so callers can identify exactly which record was chosen even when endpoints and weights match. This unit uses exact Python integer weights and excludes bool, avoiding ambiguous rounding in totals.

## Worked example: a minimum network is not a shortest route

Predict the cheapest total network, then compare its route from `a` to `c` with the direct edge. This complete enumeration needs no disjoint-set code and serves as an independent oracle for the tiny case.

```python
# A triangle has three possible spanning trees.
edges = [("a", "b", 2), ("b", "c", 2), ("a", "c", 3)]
candidates = [(0, 1), (0, 2), (1, 2)]
totals = {choice: sum(edges[index][2] for index in choice) for choice in candidates}
assert totals == {(0, 1): 4, (0, 2): 5, (1, 2): 5}
minimum_tree = (0, 1)
assert sum(edges[index][2] for index in minimum_tree) == 4
assert edges[2][2] == 3 < edges[0][2] + edges[1][2]
print("Minimum total network costs 4; its a-to-c route costs 4, versus direct cost 3.")
```

The two weight-2 edges minimize total selected weight at 4. However, their route from `a` to `c` costs 4, while the direct edge costs 3. The minimum tree optimizes a global connectivity budget. A shortest-path tree from `a` would solve a different problem and can have a higher total edge cost.

Change one edge weight to a negative integer and enumerate the three totals again. The comparison still makes sense, and Kruskal should agree. Now add an isolated vertex: no extra edge is needed for its singleton component, but the output should be called a forest rather than a tree spanning one connected graph.

## Ties, disconnected inputs and proof boundaries

Candidates are ordered by `(weight, original_index)`. Equal-weight input order determines which available edge is accepted first. Reordering tied records can therefore change the selected forest while retaining minimum cost. Deterministic tie handling is a reproducibility policy, not a claim that the optimum is unique.

The structural verifier asks two questions: are selected edges acyclic, and do they induce exactly the components present in the full graph? It intentionally does not establish minimal weight. A more expensive spanning tree still passes. On a tiny graph, enumerate subsets with the necessary edge count, compare their connectivity using independent traversal, and take the smallest total. That supplies an optimality oracle without reusing Kruskal as its own expected answer.

For large graphs, exhaustive subsets are infeasible. The algorithmic proof and more scalable certificates become important, but this unit's bounded enumeration is valuable for implementation testing. Preserve the distinction between an algorithm's mathematical guarantee under stated assumptions and the particular cases you actually executed.

## Exercises

### Six exercises

Implement these functions in `python/professional/lessons/py_algo_06.py`. Keep edge indices stable, test disconnected inputs, and compare membership before and after path compression. Avoid reconstructing graph routes from disjoint-set parent links.

1. **Create singleton components: `make_sets`.** Given a list of unique Python string vertices, return a fresh DisjointSet with each parent pointing to itself, size 1 at each root and components equal to the vertex count. Duplicate or nonstring labels raise ValueError. Empty input is valid. The public state is inspectable for learning but callers must not mutate it outside these operations.

   **Expected:** ["a", "b"] yields two singleton roots and components=2. Empty input has empty dictionaries and components=0. Two calls own independent dictionaries.

2. **Compress a path without changing connectivity: `find_root`.** For a valid API-produced DisjointSet and an existing string vertex, iteratively find the self-parented representative and compress every traversed parent link directly to it. Unknown vertices, broken encountered links or cycles raise ValueError. Return the root label; preserve root sizes and component count. Do not use recursion or scan unrelated components.

   **Expected:** After unions forming d -> c -> a, find_root(d) returns a and rewrites parent[d] to a. Component membership and root size remain unchanged.

3. **Merge smaller components and resolve ties: `union_sets`.** For a valid DisjointSet, union two existing string vertices. Return False if they already share a root; otherwise attach the smaller root under the larger root, choosing the lexicographically smaller root when sizes tie. Keep sizes only at surviving roots and decrement components exactly once. Unknown endpoints raise ValueError before mutation. Path compression may occur during valid calls.

   **Expected:** Union b with a in two singleton sets chooses root a and size 2. Repeating that union returns False without changing component count or size. A self-union is also False.

4. **Expose a canonical partition: `component_groups`.** Return a list of sorted tuples of vertex labels, one per component, with the outer list sorted lexicographically. Accept valid API-produced state, allow empty state and preserve membership, sizes and component count. Calls to find_root may compress parent links. Do not group by immediate parent when it is not the final representative.

   **Expected:** Components {a, b}, {c}, {d, e} return [("a", "b"), ("c",), ("d", "e")], independent of dictionary insertion order or intermediate parent links.

5. **Select a minimum forest with stable edge identity: `kruskal_forest`.** Accept unique string vertices and undirected edges (left, right, integer_weight), excluding bool weights and absent endpoints. Allow negative weights, self-loops, parallel edges and disconnected or empty graphs. Return (selected_original_edge_indices, exact_total_weight), processing edges by ascending (weight, original_index) and accepting only component-merging edges. Preserve inputs. Reject malformed input with ValueError.

   **Expected:** On a triangle with edge weights -2, 4 and 5, choose the first two edges for total 2. Isolated vertices remain components. Self-loops never enter the forest, even with negative weights. Equal weights follow input order.

6. **Check structural evidence without claiming optimality: `is_spanning_forest`.** Validate the same graph contract and a list of unique valid original edge indices, excluding bool. Return whether the selected edges are acyclic and induce exactly the connected components of the full undirected graph. A selected self-loop or cycle returns False; missing connectivity also returns False. Invalid indices or duplicates raise ValueError. Empty graph and empty selection return True. Do not claim this establishes minimum weight.

   **Expected:** For triangle weights 1, 2, 10, selecting the weight-1 and weight-10 edges passes this structural check despite being more expensive than the optimum. Selecting one edge fails to span the component.

## Common pitfalls

### Diagnosis, applications and retrieval

If repeated unions shrink the component count, check whether you compared representatives before updating state. If a size lookup fails, inspect whether it used a nonroot label. If a spanning check passes a cycle, compare edge count and connectivity separately. If a tie changes the chosen edges, verify the declared original-index rule before assuming a cost defect.

Disjoint sets support incremental connectivity, image-region merging and cycle detection. Minimum spanning forests support connectivity design and some clustering procedures. They do not automatically answer shortest paths, directed connectivity, or deletion of an edge from an already merged component. Deletions need a different approach because union alone discards the history needed to split a set.

## Self-check

Explain why internal parent links are not graph edges, why a negative edge is permitted, and why a valid forest need not be minimum. Then produce an isolated-vertex case and a tied parallel-edge case, including the exact expected selected indices and cost.

## Next step

Continue to [streaming summaries, order statistics and sampling](py_algo_07.md)
after its probability prerequisite is complete. Reuse canonical member groups
as an independent observation rather than depending on one internal root label.
Before applying Kruskal to a new network, state whether the objective is total
connectivity cost or routes from an origin; choose a different algorithm when
those objectives differ.

## Further reading

Python's [sorting documentation](https://docs.python.org/3.12/howto/sorting.html) explains explicit key ordering. For algorithmic reasoning, use the invariants and independent subset checks above to connect the implementation to the cut argument rather than relying on a library result alone.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-06: Disjoint Sets and Minimum Spanning Forests.
Read python/professional/companion-guides/py_algo_06.md and python/professional/lessons/py_algo_06.py. Direct prerequisites: python-algo-02, python-algo-03. Keep explanations within that boundary and introduce new vocabulary at a beginner-friendly pace.
Focus on parent forest invariant, path compression, union by size, connectivity partitions, Kruskal edge selection, spanning versus minimum evidence. Explain one mechanism, ask me to predict a concrete result, let me attempt it, give one hint at a time, then review my output, invariant, memory or exception evidence. Ask me to retrieve the explanation in my own words. Do not read solutions/ until I ask or have made an honest attempt.
For retrieval, ask me to explain why compression cannot decrement the component count, contrast internal parent links with original graph edges, and construct a spanning forest that is valid but not minimum. Ask me to justify the exact selected edge indices in a tied fixture.
Use only the Docker classroom's prepared Python Core environment, standard-library code and tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database writes, downloads or external services; do not execute live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a counterexample to an incorrect algorithm and the actual retained-state cost.
```
