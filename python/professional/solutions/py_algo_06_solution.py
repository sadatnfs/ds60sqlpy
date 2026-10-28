"""Standalone references for python-algo-06: disjoint sets and minimum forests."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DisjointSet:
    parent: dict[str, str]
    size: dict[str, int]
    components: int


def make_sets(vertices: list[str]) -> DisjointSet:
    if any(not isinstance(vertex, str) for vertex in vertices) or len(set(vertices)) != len(
        vertices
    ):
        raise ValueError("Expected unique string vertex labels")
    return DisjointSet(
        {vertex: vertex for vertex in vertices}, dict.fromkeys(vertices, 1), len(vertices)
    )


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


def component_groups(state: DisjointSet) -> list[tuple[str, ...]]:
    groups: dict[str, list[str]] = {}
    for vertex in state.parent:
        groups.setdefault(find_root(state, vertex), []).append(vertex)
    return sorted(tuple(sorted(members)) for members in groups.values())


def _validate_edges(vertices: list[str], edges: list[tuple[str, str, int]]) -> None:
    labels = set(vertices)
    for edge in edges:
        if not isinstance(edge, (tuple, list)) or len(edge) != 3:
            raise ValueError("Each edge needs two endpoints and an integer weight")
        left, right, weight = edge
        if (
            not isinstance(left, str)
            or not isinstance(right, str)
            or left not in labels
            or right not in labels
        ):
            raise ValueError("Edge endpoint is absent")
        if isinstance(weight, bool) or not isinstance(weight, int):
            raise ValueError("Expected an exact integer edge weight")


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


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    state = make_sets(["a", "b", "c", "d"])
    assert state.components == 4 and find_root(state, "c") == "c"
    assert union_sets(state, "b", "a") and find_root(state, "b") == "a"
    assert not union_sets(state, "a", "b") and state.components == 3
    assert component_groups(state) == [("a", "b"), ("c",), ("d",)]
    expect_value_error(lambda: make_sets(["a", "a"]))
    expect_value_error(lambda: find_root(state, "missing"))
    vertices = ["a", "b", "c", "d", "isolated"]
    edges = [("a", "a", -99), ("a", "b", -3), ("b", "c", 2), ("a", "c", 2), ("c", "d", 5)]
    selected, total = kruskal_forest(vertices, edges)
    assert selected == [1, 2, 4] and total == 4
    assert is_spanning_forest(vertices, edges, selected)
    assert not is_spanning_forest(vertices, edges, [1, 2])
    assert not is_spanning_forest(vertices, edges, [0, 1, 2, 4])
    assert kruskal_forest([], []) == ([], 0) and is_spanning_forest([], [], [])
    expect_value_error(lambda: kruskal_forest(["a"], [("a", "x", 1)]))
    expect_value_error(lambda: is_spanning_forest(vertices, edges, [1, 1]))
    print("python-algo-06: six disjoint-set and spanning-forest contracts passed")


if __name__ == "__main__":
    main()
