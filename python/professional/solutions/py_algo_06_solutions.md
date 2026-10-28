# python-algo-06: Explained reference solutions

Compare these answers with an honest attempt at [Disjoint Sets and Minimum Spanning Forests](../companion-guides/py_algo_06.md). The [standalone executable reference](py_algo_06_solution.py) includes all imports, type scaffolds, helpers and normal/boundary checks in `main()`. The snippets below use that shared context and match the six learner contracts.

## Exercise 1: Create singleton components

**Contract: `make_sets`.** Given a list of unique Python string vertices, return a fresh DisjointSet with each parent pointing to itself, size 1 at each root and components equal to the vertex count. Duplicate or nonstring labels raise ValueError. Empty input is valid. The public state is inspectable for learning but callers must not mutate it outside these operations.

**Expected:** ["a", "b"] yields two singleton roots and components=2. Empty input has empty dictionaries and components=0. Two calls own independent dictionaries.

```python
def make_sets(vertices: list[str]) -> DisjointSet:
    if any(not isinstance(vertex, str) for vertex in vertices) or len(set(vertices)) != len(
        vertices
    ):
        raise ValueError("Expected unique string vertex labels")
    return DisjointSet(
        {vertex: vertex for vertex in vertices}, {vertex: 1 for vertex in vertices}, len(vertices)
    )
```

Initialization establishes all invariants simultaneously: every label has a parent, roots are self-parented, and sizes exist only for roots. A component count avoids rescanning state after every union. The implementation copies identities into its own dictionaries rather than retaining the caller's vertex list. Duplicate labels must fail instead of silently reducing the intended graph size.

## Exercise 2: Compress a path without changing connectivity

**Contract: `find_root`.** For a valid API-produced DisjointSet and an existing string vertex, iteratively find the self-parented representative and compress every traversed parent link directly to it. Unknown vertices, broken encountered links or cycles raise ValueError. Return the root label; preserve root sizes and component count. Do not use recursion or scan unrelated components.

**Expected:** After unions forming d -> c -> a, find_root(d) returns a and rewrites parent[d] to a. Component membership and root size remain unchanged.

```python
def find_root(state: DisjointSet, vertex: str) -> str:
    if not isinstance(vertex, str) or vertex not in state.parent:
        raise ValueError("Unknown vertex")
    current = vertex
    steps = 0
    while True:
        if current not in state.parent:
            raise ValueError("Broken parent link")
        parent = state.parent[current]
        if parent == current:
            break
        current = parent
        steps += 1
        if steps > len(state.parent):
            raise ValueError("Cyclic parent links")
    root = current
    while state.parent[vertex] != vertex:
        parent = state.parent[vertex]
        state.parent[vertex] = root
        vertex = parent
    return root
```

First walk to a root, then walk the original path again while rewriting each link. Saving the old next pointer before assignment is essential. Compression changes representation, not the represented equivalence relation. The cycle guard prevents a corrupted encountered chain from looping, but this function is not a full validator for arbitrary externally edited size tables.

## Exercise 3: Merge smaller components and resolve ties

**Contract: `union_sets`.** For a valid DisjointSet, union two existing string vertices. Return False if they already share a root; otherwise attach the smaller root under the larger root, choosing the lexicographically smaller root when sizes tie. Keep sizes only at surviving roots and decrement components exactly once. Unknown endpoints raise ValueError before mutation. Path compression may occur during valid calls.

**Expected:** Union b with a in two singleton sets chooses root a and size 2. Repeating that union returns False without changing component count or size. A self-union is also False.

```python
def union_sets(state: DisjointSet, left: str, right: str) -> bool:
    if (
        not isinstance(left, str)
        or not isinstance(right, str)
        or left not in state.parent
        or right not in state.parent
    ):
        raise ValueError("Unknown union endpoint")
    first, second = find_root(state, left), find_root(state, right)
    if first == second:
        return False
    if state.size[first] < state.size[second] or (
        state.size[first] == state.size[second] and first > second
    ):
        first, second = second, first
    state.parent[second] = first
    state.size[first] += state.size.pop(second)
    state.components -= 1
    return True
```

Compare sizes of representatives, never sizes at arbitrary member labels. A losing root ceases to own a size entry after attachment. The tie rule makes the visible representation deterministic for this algorithm, but a representative is still an implementation detail rather than a permanent business identifier. Union by size keeps paths short even before compression.

## Exercise 4: Expose a canonical partition

**Contract: `component_groups`.** Return a list of sorted tuples of vertex labels, one per component, with the outer list sorted lexicographically. Accept valid API-produced state, allow empty state and preserve membership, sizes and component count. Calls to find_root may compress parent links. Do not group by immediate parent when it is not the final representative.

**Expected:** Components {a, b}, {c}, {d, e} return [("a", "b"), ("c",), ("d", "e")], independent of dictionary insertion order or intermediate parent links.

```python
def component_groups(state: DisjointSet) -> list[tuple[str, ...]]:
    groups: dict[str, list[str]] = {}
    for vertex in state.parent:
        groups.setdefault(find_root(state, vertex), []).append(vertex)
    return sorted(tuple(sorted(members)) for members in groups.values())
```

Canonical groups make observable connectivity independent of root choices. Every vertex appears exactly once. Following only one parent pointer can split a component that still contains multiple levels. This reporting function is not constant time: it visits every vertex and sorts the resulting groups. State complexity and report complexity must be described separately.

## Exercise 5: Select a minimum forest with stable edge identity

**Contract: `kruskal_forest`.** Accept unique string vertices and undirected edges (left, right, integer_weight), excluding bool weights and absent endpoints. Allow negative weights, self-loops, parallel edges and disconnected or empty graphs. Return (selected_original_edge_indices, exact_total_weight), processing edges by ascending (weight, original_index) and accepting only component-merging edges. Preserve inputs. Reject malformed input with ValueError.

**Expected:** On a triangle with edge weights -2, 4 and 5, choose the first two edges for total 2. Isolated vertices remain components. Self-loops never enter the forest, even with negative weights. Equal weights follow input order.

```python
def kruskal_forest(vertices: list[str], edges: list[tuple[str, str, int]]) -> tuple[list[int], int]:
    state = make_sets(vertices)
    _validate_edges(vertices, edges)
    selected = []
    total = 0
    for index in sorted(range(len(edges)), key=lambda item: (edges[item][2], item)):
        left, right, weight = edges[index]
        if union_sets(state, left, right):
            selected.append(index)
            total += weight
    return selected, total
```

Sorting creates a candidate order; union-find tells whether a candidate would close a cycle. The cut property justifies accepting a light edge between current components. Original indices preserve distinct parallel edges without inventing identity from endpoint pairs. Equal-weight reordering may change the chosen minimum forest while preserving optimal weight. A disconnected graph has a minimum spanning forest, not one spanning tree.

## Exercise 6: Check structural evidence without claiming optimality

**Contract: `is_spanning_forest`.** Validate the same graph contract and a list of unique valid original edge indices, excluding bool. Return whether the selected edges are acyclic and induce exactly the connected components of the full undirected graph. A selected self-loop or cycle returns False; missing connectivity also returns False. Invalid indices or duplicates raise ValueError. Empty graph and empty selection return True. Do not claim this establishes minimum weight.

**Expected:** For triangle weights 1, 2, 10, selecting the weight-1 and weight-10 edges passes this structural check despite being more expensive than the optimum. Selecting one edge fails to span the component.

```python
def is_spanning_forest(
    vertices: list[str], edges: list[tuple[str, str, int]], selected: list[int]
) -> bool:
    complete, chosen = make_sets(vertices), make_sets(vertices)
    _validate_edges(vertices, edges)
    if any(
        isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(edges)
        for index in selected
    ):
        raise ValueError("Selected edge indices must be valid integers")
    if len(set(selected)) != len(selected):
        raise ValueError("Selected edge indices must be unique")
    for left, right, _ in edges:
        union_sets(complete, left, right)
    for index in selected:
        left, right, _ = edges[index]
        if not union_sets(chosen, left, right):
            return False
    return component_groups(complete) == component_groups(chosen)
```

A spanning forest is a structural certificate: no cycles and no missing input-component connections. It does not compare alternative weights. Build full and selected partitions and compare canonical groups after rejecting cycle-forming selections. Independent brute-force enumeration on tiny graphs can establish the minimum objective; this deliberately separates feasibility from optimality evidence.

## Independent checks and limits

The reference main exercises every named contract. `tests/test_python_algorithm_modernization.py` adds independent oracles, including explicit graph reachability and exhaustive tiny spanning forests, centered rational moment calculations, sorted-prefix medians and exhaustive reservoir draw paths. Source-level contract checks are separate from semantic execution. A passing reference demonstrates tested behavior, not mastery; explain the invariant and construct a counterexample to a tempting incorrect implementation.
