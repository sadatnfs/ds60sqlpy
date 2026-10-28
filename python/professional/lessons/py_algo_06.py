"""python-algo-06: Disjoint Sets and Minimum Spanning Forests.

Run the worked examples, then implement the six contracts.
Complete answers belong in the reference area.
"""

from dataclasses import dataclass


@dataclass
class DisjointSet:
    parent: dict[str, str]
    size: dict[str, int]
    components: int


def make_sets(vertices: list[str]) -> DisjointSet:
    """
    Given a list of unique Python string vertices, return a fresh DisjointSet with each
    parent pointing to itself, size 1 at each root and components equal to the vertex count.
    Duplicate or nonstring labels raise ValueError. Empty input is valid. The public state
    is inspectable for learning but callers must not mutate it outside these operations.
    """
    raise NotImplementedError("Implement make_sets")


def find_root(state: DisjointSet, vertex: str) -> str:
    """
    For a valid API-produced DisjointSet and an existing string vertex, iteratively find the
    self-parented representative and compress every traversed parent link directly to it.
    Unknown vertices, broken encountered links or cycles raise ValueError. Return the root
    label; preserve root sizes and component count. Do not use recursion or scan unrelated
    components.
    """
    raise NotImplementedError("Implement find_root")


def union_sets(state: DisjointSet, left: str, right: str) -> bool:
    """
    For a valid DisjointSet, union two existing string vertices. Return False if they
    already share a root; otherwise attach the smaller root under the larger root, choosing
    the lexicographically smaller root when sizes tie. Keep sizes only at surviving roots
    and decrement components exactly once. Unknown endpoints raise ValueError before
    mutation. Path compression may occur during valid calls.
    """
    raise NotImplementedError("Implement union_sets")


def component_groups(state: DisjointSet) -> list[tuple[str, ...]]:
    """
    Return a list of sorted tuples of vertex labels, one per component, with the outer list
    sorted lexicographically. Accept valid API-produced state, allow empty state and
    preserve membership, sizes and component count. Calls to find_root may compress parent
    links. Do not group by immediate parent when it is not the final representative.
    """
    raise NotImplementedError("Implement component_groups")


def kruskal_forest(vertices: list[str], edges: list[tuple[str, str, int]]) -> tuple[list[int], int]:
    """
    Accept unique string vertices and undirected edges (left, right, integer_weight),
    excluding bool weights and absent endpoints. Allow negative weights, self-loops,
    parallel edges and disconnected or empty graphs. Return (selected_original_edge_indices,
    exact_total_weight), processing edges by ascending (weight, original_index) and
    accepting only component-merging edges. Preserve inputs. Reject malformed input with
    ValueError.
    """
    raise NotImplementedError("Implement kruskal_forest")


def is_spanning_forest(
    vertices: list[str], edges: list[tuple[str, str, int]], selected: list[int]
) -> bool:
    """
    Validate the same graph contract and a list of unique valid original edge indices,
    excluding bool. Return whether the selected edges are acyclic and induce exactly the
    connected components of the full undirected graph. A selected self-loop or cycle returns
    False; missing connectivity also returns False. Invalid indices or duplicates raise
    ValueError. Empty graph and empty selection return True. Do not claim this establishes
    minimum weight.
    """
    raise NotImplementedError("Implement is_spanning_forest")


def worked_examples() -> None:
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

    # A triangle has three possible spanning trees.
    edges = [("a", "b", 2), ("b", "c", 2), ("a", "c", 3)]
    candidates = [(0, 1), (0, 2), (1, 2)]
    totals = {choice: sum(edges[index][2] for index in choice) for choice in candidates}
    assert totals == {(0, 1): 4, (0, 2): 5, (1, 2): 5}
    minimum_tree = (0, 1)
    assert sum(edges[index][2] for index in minimum_tree) == 4
    assert edges[2][2] == 3 < edges[0][2] + edges[1][2]
    print("Minimum total network costs 4; its a-to-c route costs 4, versus direct cost 3.")


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement all six contracts and record boundary evidence.")

# Exercise 1: Create singleton components
# Contract: make_sets
# Prompt: Given a list of unique Python string vertices, return a fresh DisjointSet with each
# parent pointing to itself, size 1 at each root and components equal to the vertex count.
# Duplicate or nonstring labels raise ValueError. Empty input is valid. The public state is
# inspectable for learning but callers must not mutate it outside these operations.
# Expected: ["a", "b"] yields two singleton roots and components=2. Empty input has empty
# dictionaries and components=0. Two calls own independent dictionaries.

# Exercise 2: Compress a path without changing connectivity
# Contract: find_root
# Prompt: For a valid API-produced DisjointSet and an existing string vertex, iteratively find the
# self-parented representative and compress every traversed parent link directly to it. Unknown
# vertices, broken encountered links or cycles raise ValueError. Return the root label; preserve
# root sizes and component count. Do not use recursion or scan unrelated components.
# Expected: After unions forming d -> c -> a, find_root(d) returns a and rewrites parent[d] to a.
# Component membership and root size remain unchanged.

# Exercise 3: Merge smaller components and resolve ties
# Contract: union_sets
# Prompt: For a valid DisjointSet, union two existing string vertices. Return False if they
# already share a root; otherwise attach the smaller root under the larger root, choosing the
# lexicographically smaller root when sizes tie. Keep sizes only at surviving roots and decrement
# components exactly once. Unknown endpoints raise ValueError before mutation. Path compression
# may occur during valid calls.
# Expected: Union b with a in two singleton sets chooses root a and size 2. Repeating that union
# returns False without changing component count or size. A self-union is also False.

# Exercise 4: Expose a canonical partition
# Contract: component_groups
# Prompt: Return a list of sorted tuples of vertex labels, one per component, with the outer list
# sorted lexicographically. Accept valid API-produced state, allow empty state and preserve
# membership, sizes and component count. Calls to find_root may compress parent links. Do not
# group by immediate parent when it is not the final representative.
# Expected: Components {a, b}, {c}, {d, e} return [("a", "b"), ("c",), ("d", "e")], independent of
# dictionary insertion order or intermediate parent links.

# Exercise 5: Select a minimum forest with stable edge identity
# Contract: kruskal_forest
# Prompt: Accept unique string vertices and undirected edges (left, right, integer_weight),
# excluding bool weights and absent endpoints. Allow negative weights, self-loops, parallel edges
# and disconnected or empty graphs. Return (selected_original_edge_indices, exact_total_weight),
# processing edges by ascending (weight, original_index) and accepting only component-merging
# edges. Preserve inputs. Reject malformed input with ValueError.
# Expected: On a triangle with edge weights -2, 4 and 5, choose the first two edges for total 2.
# Isolated vertices remain components. Self-loops never enter the forest, even with negative
# weights. Equal weights follow input order.

# Exercise 6: Check structural evidence without claiming optimality
# Contract: is_spanning_forest
# Prompt: Validate the same graph contract and a list of unique valid original edge indices,
# excluding bool. Return whether the selected edges are acyclic and induce exactly the connected
# components of the full undirected graph. A selected self-loop or cycle returns False; missing
# connectivity also returns False. Invalid indices or duplicates raise ValueError. Empty graph and
# empty selection return True. Do not claim this establishes minimum weight.
# Expected: For triangle weights 1, 2, 10, selecting the weight-1 and weight-10 edges passes this
# structural check despite being more expensive than the optimum. Selecting one edge fails to span
# the component.
