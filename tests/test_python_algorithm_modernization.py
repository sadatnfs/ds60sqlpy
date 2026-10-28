"""Independent structural, graph, rational and sampling checks for algorithm units."""

import ast
import copy
import importlib.util
import math
import random
import re
import sys
import tracemalloc
from collections import Counter, deque
from collections.abc import Callable, Iterable, Iterator, Sequence
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from types import ModuleType
from typing import Any, Generic, TypeVar

import pytest

ROOT = Path(__file__).resolve().parents[1]
T = TypeVar("T")
Edge = tuple[str, str, int]


def _load(number: int) -> ModuleType:
    path = ROOT / "python/professional/solutions" / f"py_algo_{number:02d}_solution.py"
    name = f"algorithm_modernization_{number}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


trees, forests, streaming = [_load(number) for number in range(5, 8)]


class OnePass(Generic[T]):
    def __init__(self, values: Iterable[T]) -> None:
        self.values = iter(values)
        self.iterations = 0
        self.consumed = 0

    def __iter__(self) -> Iterator[T]:
        self.iterations += 1
        if self.iterations != 1:
            raise AssertionError("Input was iterated more than once")
        for value in self.values:
            self.consumed += 1
            yield value


def test_tree_identity_is_not_payload_equality() -> None:
    root = trees.Node(4, trees.Node(4), trees.Node(4))
    assert trees.validate_tree(root) == 3
    assert trees.preorder(root) == [4, 4, 4]
    assert not trees.is_strict_bst(root)
    shared = trees.Node(4)
    with pytest.raises(ValueError, match="shared"):
        trees.validate_tree(trees.Node(9, shared, shared))


@pytest.mark.parametrize(
    "function", [trees.validate_tree, trees.preorder, trees.tree_height, trees.is_strict_bst]
)
def test_tree_operations_reject_cycles_and_preserve_links(
    function: Callable[[object], object],
) -> None:
    root, child = trees.Node(1), trees.Node(2)
    root.right = child
    child.left = root
    with pytest.raises(ValueError):
        function(root)
    assert root.right is child and child.left is root


def test_iterative_tree_operations_handle_deep_chains() -> None:
    root = None
    for value in reversed(range(3000)):
        root = trees.Node(value, None, root)
    assert trees.validate_tree(root) == 3000
    assert trees.tree_height(root) == 3000
    assert trees.preorder(root) == list(range(3000))
    assert trees.is_strict_bst(root)


def test_preorder_height_and_ancestor_bounds() -> None:
    root = trees.Node(8, trees.Node(3, trees.Node(1), trees.Node(6)), trees.Node(10))
    assert trees.preorder(root) == [8, 3, 1, 6, 10]
    assert trees.tree_height(root) == 3
    assert trees.is_strict_bst(root)
    assert not trees.is_strict_bst(trees.Node(8, trees.Node(3, None, trees.Node(9))))
    assert not trees.is_strict_bst(trees.Node(8, None, trees.Node(10, trees.Node(7))))
    assert trees.is_strict_bst(trees.Node(0, trees.Node(-(2**200)), trees.Node(2**200)))
    assert trees.validate_tree(None) == trees.tree_height(None) == 0
    assert trees.preorder(None) == [] and trees.is_strict_bst(None)


@pytest.mark.parametrize("root", [trees.Node(True), trees.Node(2, "bad"), "not a node"])
def test_malformed_tree_payload_or_child(root: object) -> None:
    with pytest.raises(ValueError):
        trees.validate_tree(root)


def test_trie_queries_match_independent_string_filter_and_ownership() -> None:
    words = ["", "car", "cart", "cat", "café", "cafe\u0301", "Car", "car", "🦉nest"]
    source = OnePass(words)
    root = trees.build_trie(source)
    assert source.consumed == len(words)
    other = trees.build_trie(words)
    assert root is not other and root.children is not other.children
    for prefix in ["", "ca", "car", "café", "cafe", "🦉", "none"]:
        for limit in [0, 1, 2, 20]:
            expected = sorted({word for word in words if word.startswith(prefix)})[:limit]
            assert trees.prefix_words(root, prefix, limit) == expected
    assert trees.prefix_words(trees.build_trie([]), "", 3) == []
    assert trees.prefix_words(trees.build_trie([""]), "", 3) == [""]


def test_trie_rejects_cycles_shared_nodes_and_bad_edge_labels() -> None:
    root = trees.TrieNode()
    root.children["a"] = root
    with pytest.raises(ValueError):
        trees.prefix_words(root, "", 0)
    shared = trees.TrieNode(terminal=True)
    with pytest.raises(ValueError):
        trees.prefix_words(trees.TrieNode({"a": shared, "b": shared}), "", 2)
    with pytest.raises(ValueError):
        trees.prefix_words(trees.TrieNode({"ab": trees.TrieNode()}), "", 2)
    with pytest.raises(ValueError):
        trees.build_trie(["fine", 3])
    with pytest.raises(ValueError):
        trees.prefix_words(trees.build_trie([]), "", True)


def _components(vertices: Sequence[str], edges: Sequence[Edge]) -> list[tuple[str, ...]]:
    adjacency: dict[str, set[str]] = {vertex: set() for vertex in vertices}
    for left, right, _ in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(vertices)
    components = []
    while remaining:
        start = min(remaining)
        found = {start}
        pending = deque([start])
        while pending:
            for neighbor in adjacency[pending.popleft()]:
                if neighbor not in found:
                    found.add(neighbor)
                    pending.append(neighbor)
        remaining -= found
        components.append(tuple(sorted(found)))
    return sorted(components)


def _minimum_weight_by_subsets(vertices: Sequence[str], edges: Sequence[Edge]) -> int:
    target = _components(vertices, edges)
    needed = len(vertices) - len(target)
    costs = []
    for indices in combinations(range(len(edges)), needed):
        chosen = [edges[index] for index in indices]
        if _components(vertices, chosen) == target:
            costs.append(sum(edge[2] for edge in chosen))
    return min(costs)


def test_union_by_size_path_compression_and_canonical_partition() -> None:
    state = forests.make_sets(["d", "c", "b", "a", "isolated"])
    assert forests.union_sets(state, "a", "b")
    assert forests.union_sets(state, "c", "d")
    assert forests.union_sets(state, "c", "a")
    assert state.parent["d"] == "c" and state.parent["c"] == "a"
    original_sizes = state.size.copy()
    assert forests.find_root(state, "d") == "a"
    assert state.parent["d"] == "a" and state.size == original_sizes == {"a": 4, "isolated": 1}
    assert state.components == 2
    assert forests.component_groups(state) == [("a", "b", "c", "d"), ("isolated",)]
    assert not forests.union_sets(state, "b", "d")
    assert not forests.union_sets(state, "a", "a") and state.components == 2
    before = copy.deepcopy(state)
    with pytest.raises(ValueError):
        forests.union_sets(state, "d", "missing")
    assert state == before


def test_connectivity_after_each_union_matches_bfs() -> None:
    vertices = list("abcde")
    state = forests.make_sets(vertices)
    edges: list[Edge] = []
    for left, right in [("a", "b"), ("c", "d"), ("b", "c"), ("a", "d"), ("e", "e")]:
        before = len(_components(vertices, edges))
        edges.append((left, right, 1))
        expected = _components(vertices, edges)
        assert forests.union_sets(state, left, right) == (len(expected) < before)
        assert forests.component_groups(state) == expected
        assert state.components == len(expected)
        assert sum(state.size.values()) == len(vertices)


@pytest.mark.parametrize(
    "vertices,edges",
    [
        ([], []),
        (["alone"], []),
        (list("abc"), [("a", "b", -2), ("b", "c", 4), ("a", "c", 5)]),
        (list("abcd"), [("a", "b", -4), ("c", "d", 2), ("a", "a", -100)]),
        (list("abc"), [("a", "b", 3), ("b", "a", 1), ("b", "c", 2), ("a", "c", 2)]),
    ],
)
def test_kruskal_matches_exhaustive_small_graph_oracle(
    vertices: list[str], edges: list[Edge]
) -> None:
    original = copy.deepcopy(edges)
    selected, total = forests.kruskal_forest(vertices, edges)
    assert total == _minimum_weight_by_subsets(vertices, edges)
    assert total == sum(edges[index][2] for index in selected)
    assert forests.is_spanning_forest(vertices, edges, selected)
    assert len(selected) == len(vertices) - len(_components(vertices, edges))
    assert edges == original


def test_kruskal_many_deterministic_small_graphs_against_exhaustive_oracle() -> None:
    rng = random.Random(84)
    vertices = list("abcd")
    pairs = list(combinations(vertices, 2))
    for _ in range(30):
        edges = [(left, right, rng.randrange(-4, 5)) for left, right in pairs if rng.random() < 0.7]
        selected, total = forests.kruskal_forest(vertices, edges)
        assert total == _minimum_weight_by_subsets(vertices, edges)
        assert forests.is_spanning_forest(vertices, edges, selected)


def test_tie_identity_and_feasibility_do_not_claim_minimum() -> None:
    vertices = list("abc")
    tied = [("a", "b", 1), ("a", "b", 1), ("a", "c", 1), ("b", "c", 1)]
    assert forests.kruskal_forest(vertices, tied) == ([0, 2], 2)
    weighted = [("a", "b", 1), ("b", "c", 2), ("a", "c", 10)]
    assert forests.is_spanning_forest(vertices, weighted, [0, 2])
    assert forests.kruskal_forest(vertices, weighted)[1] == 3
    assert not forests.is_spanning_forest(vertices, weighted, [0])
    assert not forests.is_spanning_forest(vertices, weighted, [0, 1, 2])
    with pytest.raises(ValueError):
        forests.is_spanning_forest(vertices, weighted, [0, 0])


@pytest.mark.parametrize(
    "vertices,edges",
    [
        (["a", "a"], []),
        (["a", 1], []),
        (["a"], [("a", "missing", 2)]),
        (["a"], [("a", "a", True)]),
        (["a"], [("a", "a", 1.0)]),
    ],
)
def test_forest_input_boundaries(
    vertices: list[object], edges: list[tuple[object, object, object]]
) -> None:
    with pytest.raises(ValueError):
        forests.kruskal_forest(vertices, edges)


def test_moments_match_centered_exact_oracle_and_one_pass() -> None:
    values = [2**40 + step for step in [1, 3, 5, 7]]
    expected_mean = Fraction(sum(values), len(values))
    expected_m2 = sum((Fraction(value) - expected_mean) ** 2 for value in values)
    source = OnePass(values)
    count, mean, m2 = streaming.moments(source)
    assert source.consumed == count == 4
    assert math.isclose(mean, float(expected_mean), rel_tol=0, abs_tol=1e-10)
    assert math.isclose(m2, float(expected_m2), rel_tol=0, abs_tol=1e-10)
    assert streaming.sample_variance((count, mean, m2)) == float(expected_m2 / 3)
    assert streaming.moments([]) == (0, 0.0, 0.0)
    assert streaming.sample_variance(streaming.moments([])) is None
    assert streaming.sample_variance(streaming.moments([9])) is None
    assert streaming.sample_variance(streaming.moments([9, 9])) == 0


def test_merge_unequal_chunks_empty_identity_and_partition_orders() -> None:
    values = [10, 10, 20, 20, 20, 20]
    expected_mean = Fraction(50, 3)
    expected_m2 = Fraction(400, 3)
    for split in range(len(values) + 1):
        left, right = streaming.moments(values[:split]), streaming.moments(values[split:])
        for merged in [streaming.merge_moments(left, right), streaming.merge_moments(right, left)]:
            assert merged[0] == len(values)
            assert math.isclose(merged[1], float(expected_mean), rel_tol=1e-14)
            assert math.isclose(merged[2], float(expected_m2), rel_tol=1e-14)
    one, two, three = (streaming.moments(part) for part in [values[:1], values[1:3], values[3:]])
    first = streaming.merge_moments(streaming.merge_moments(one, two), three)
    second = streaming.merge_moments(one, streaming.merge_moments(two, three))
    assert math.isclose(first[2], second[2], rel_tol=1e-14)


@pytest.mark.parametrize(
    "state",
    [
        (True, 0.0, 0.0),
        (-1, 0.0, 0.0),
        (0, 4.0, 0.0),
        (1, 2.0, 1.0),
        (3, math.inf, 0.0),
        (3, 0.0, -1.0),
    ],
)
def test_invalid_moment_state_is_rejected(state: tuple[int, float, float]) -> None:
    with pytest.raises(ValueError):
        streaming.sample_variance(state)
    with pytest.raises(ValueError):
        streaming.merge_moments(state, (0, 0.0, 0.0))


@pytest.mark.parametrize("values", [[True], [math.nan], [math.inf], [1e308, -1e308], [10**1000]])
def test_invalid_or_unrepresentable_updates(values: list[int | float]) -> None:
    with pytest.raises(ValueError):
        streaming.moments(values)


def test_top_k_matches_stable_sort_including_large_integer_scores() -> None:
    records = [(5, "z"), (8, "best"), (5, "a"), (5, "b"), (-(2**200), "low"), (2**200, "high")]
    for k in [0, 1, 3, len(records), len(records) + 1]:
        source = OnePass(records)
        assert (
            streaming.stable_top_k(source, k)
            == sorted(records, key=lambda item: item[0], reverse=True)[:k]
        )
        assert source.consumed == len(records)
    with pytest.raises(ValueError):
        streaming.stable_top_k([(True, "bad")], 0)


def test_bounded_top_k_and_reservoir_do_not_materialize_payload_stream() -> None:
    operations: list[Callable[[], Any]] = [
        lambda: streaming.stable_top_k(
            ((index % 11, f"{index}:" + "x" * 512) for index in range(20_000)), 7
        ),
        lambda: streaming.reservoir_sample(
            (f"{index}:" + "x" * 512 for index in range(20_000)), 7, random.Random(11)
        ),
    ]
    for operation in operations:
        tracemalloc.start()
        try:
            result = operation()
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert len(result) == 7
        # Materializing this input retains over 10 MiB. Allow 2 MiB for runtime variation.
        assert peak < 2_000_000


def test_prefix_medians_match_exact_sorted_prefix_oracle() -> None:
    values = [2**100, 2**100 + 1, -7, -7, 20, 0, 20]
    source = OnePass(values)
    medians = streaming.prefix_medians(source)
    assert source.consumed == 0
    expected = []
    for length in range(1, len(values) + 1):
        ordered = sorted(values[:length])
        expected.append(
            Fraction(ordered[length // 2])
            if length % 2
            else Fraction(ordered[length // 2 - 1] + ordered[length // 2], 2)
        )
    assert list(medians) == expected
    assert source.consumed == len(values)
    assert list(streaming.prefix_medians([])) == []
    with pytest.raises(ValueError):
        list(streaming.prefix_medians([1, True]))


def test_reservoir_uniform_subsets_by_exhaustive_draw_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counts: Counter[tuple[str, ...]] = Counter()
    for choices in product(range(3), range(4)):
        draws = iter(choices)
        rng = random.Random(0)
        bounds: list[int] = []

        def draw(
            stop: int, recorded_bounds: list[int] = bounds, remaining_draws: Iterator[int] = draws
        ) -> int:
            recorded_bounds.append(stop)
            value = next(remaining_draws)
            assert 0 <= value < stop
            return value

        monkeypatch.setattr(rng, "randrange", draw)
        sample = streaming.reservoir_sample("abcd", 2, rng)
        counts[tuple(sorted(sample))] += 1
        assert bounds == [3, 4]
    assert counts == Counter(dict.fromkeys(combinations("abcd", 2), 2))


def test_reservoir_replay_zero_short_input_and_object_ownership() -> None:
    rng = random.Random(991)
    saved = rng.getstate()
    first = streaming.reservoir_sample(range(100), 7, rng)
    rng.setstate(saved)
    assert streaming.reservoir_sample(range(100), 7, rng) == first
    assert len(set(first)) == 7
    before = rng.getstate()
    source = OnePass(range(30))
    assert streaming.reservoir_sample(source, 0, rng) == []
    assert source.consumed == 30 and rng.getstate() == before
    value = {"count": 1}
    sample = streaming.reservoir_sample([value], 3, rng)
    value["count"] = 9
    assert sample[0] is value and sample[0]["count"] == 9
    assert rng.getstate() == before
    with pytest.raises(ValueError):
        streaming.reservoir_sample([], True, rng)
    with pytest.raises(ValueError):
        streaming.reservoir_sample([], 1, random.SystemRandom())


@pytest.mark.parametrize("number", [5, 6, 7])
def test_six_named_contracts_and_answer_free_learner_artifacts(number: int) -> None:
    stem = f"py_algo_{number:02d}"
    base = ROOT / "python/professional"
    learner = (base / "lessons" / f"{stem}.py").read_text()
    guide = (base / "companion-guides" / f"{stem}.md").read_text()
    explanation = (base / "solutions" / f"{stem}_solutions.md").read_text()
    reference = ast.parse((base / "solutions" / f"{stem}_solution.py").read_text())
    reference_functions = {
        node.name: node for node in reference.body if isinstance(node, ast.FunctionDef)
    }
    contracts = [
        node
        for node in ast.parse(learner).body
        if isinstance(node, ast.FunctionDef) and node.name != "worked_examples"
    ]
    assert len(contracts) == 6
    for node in contracts:
        assert isinstance(node.body[-1], ast.Raise)
        assert ast.dump(node.args) == ast.dump(reference_functions[node.name].args)
        assert node.name in guide and node.name in explanation
    assert len(re.findall(r"^# Exercise [1-6]:", learner, re.MULTILINE)) == 6
    assert len(re.findall(r"^[1-6]\. \*\*", guide, re.MULTILINE)) == 6
    assert len(re.findall(r"^## Exercise [1-6]:", explanation, re.MULTILINE)) == 6
    assert len(re.findall(r"```python\n", guide)) == 2
    assert "## Ask an AI tutor about this lesson" in guide
    assert "$guide-ds60sqlpy-learning" in guide and guide.rstrip().endswith("```")
    assert "\N{EM DASH}" not in learner + guide + explanation
