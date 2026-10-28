"""Standalone references for python-algo-05: trees, strict ordering and tries."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field


@dataclass(eq=False)
class Node:
    value: int
    left: Node | None = None
    right: Node | None = None


@dataclass(eq=False)
class TrieNode:
    children: dict[str, TrieNode] = field(default_factory=dict)
    terminal: bool = False


def validate_tree(root: Node | None) -> int:
    pending = [] if root is None else [root]
    seen: set[int] = set()
    while pending:
        node = pending.pop()
        if (
            not isinstance(node, Node)
            or isinstance(node.value, bool)
            or not isinstance(node.value, int)
        ):
            raise ValueError("Expected integer-valued Node objects")
        if id(node) in seen:
            raise ValueError("A cycle or shared child violates tree ownership")
        seen.add(id(node))
        if node.right is not None:
            pending.append(node.right)
        if node.left is not None:
            pending.append(node.left)
    return len(seen)


def preorder(root: Node | None) -> list[int]:
    validate_tree(root)
    pending = [] if root is None else [root]
    result = []
    while pending:
        node = pending.pop()
        result.append(node.value)
        if node.right is not None:
            pending.append(node.right)
        if node.left is not None:
            pending.append(node.left)
    return result


def tree_height(root: Node | None) -> int:
    validate_tree(root)
    pending = [] if root is None else [(root, 1)]
    height = 0
    while pending:
        node, depth = pending.pop()
        height = max(height, depth)
        if node.right is not None:
            pending.append((node.right, depth + 1))
        if node.left is not None:
            pending.append((node.left, depth + 1))
    return height


def is_strict_bst(root: Node | None) -> bool:
    validate_tree(root)
    pending: list[tuple[Node, int | None, int | None]] = (
        [] if root is None else [(root, None, None)]
    )
    while pending:
        node, lower, upper = pending.pop()
        if (lower is not None and node.value <= lower) or (
            upper is not None and node.value >= upper
        ):
            return False
        if node.left is not None:
            pending.append((node.left, lower, node.value))
        if node.right is not None:
            pending.append((node.right, node.value, upper))
    return True


def build_trie(words: Iterable[str]) -> TrieNode:
    root = TrieNode()
    for word in words:
        if not isinstance(word, str):
            raise ValueError("Trie words must be strings")
        node = root
        for character in word:
            node = node.children.setdefault(character, TrieNode())
        node.terminal = True
    return root


def _validate_trie(root: TrieNode) -> None:
    pending = [root]
    seen: set[int] = set()
    while pending:
        node = pending.pop()
        if (
            not isinstance(node, TrieNode)
            or type(node.terminal) is not bool
            or not isinstance(node.children, dict)
        ):
            raise ValueError("Malformed trie node")
        if id(node) in seen:
            raise ValueError("Trie must not contain cycles or shared children")
        seen.add(id(node))
        for character, child in node.children.items():
            if not isinstance(character, str) or len(character) != 1:
                raise ValueError("Trie edges must be single Unicode code points")
            pending.append(child)


def prefix_words(root: TrieNode, prefix: str, limit: int) -> list[str]:
    if (
        not isinstance(prefix, str)
        or isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit < 0
    ):
        raise ValueError("Expected a string prefix and nonnegative integer limit")
    _validate_trie(root)
    if limit == 0:
        return []
    node = root
    for character in prefix:
        if character not in node.children:
            return []
        node = node.children[character]
    result: list[str] = []
    pending = [(node, prefix)]
    while pending and len(result) < limit:
        node, word = pending.pop()
        if node.terminal:
            result.append(word)
        for character in sorted(node.children, reverse=True):
            pending.append((node.children[character], word + character))
    return result


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    root = Node(8, Node(3, Node(1), Node(6)), Node(10))
    assert validate_tree(root) == 5 and validate_tree(None) == 0
    assert preorder(root) == [8, 3, 1, 6, 10] and preorder(None) == []
    assert tree_height(root) == 3 and tree_height(None) == 0
    assert is_strict_bst(root) and is_strict_bst(None)
    assert not is_strict_bst(Node(8, Node(3, None, Node(9))))
    assert not is_strict_bst(Node(8, Node(8)))
    shared = Node(2)
    expect_value_error(lambda: validate_tree(Node(1, shared, shared)))
    cycle = Node(1)
    cycle.left = cycle
    expect_value_error(lambda: tree_height(cycle))
    trie = build_trie(["", "car", "cat", "car", "café", "Cafe"])
    assert prefix_words(trie, "ca", 10) == ["café", "car", "cat"]
    assert prefix_words(trie, "", 2) == ["", "Cafe"]
    assert prefix_words(trie, "car", 10) == ["car"]
    assert prefix_words(trie, "missing", 10) == []
    assert prefix_words(build_trie([]), "", 10) == []
    expect_value_error(lambda: build_trie(["ok", 4]))  # type: ignore[list-item]  # Reject a non-string word.
    expect_value_error(lambda: prefix_words(trie, "", -1))
    print("python-algo-05: six structural and prefix-search contracts passed")


if __name__ == "__main__":
    main()
