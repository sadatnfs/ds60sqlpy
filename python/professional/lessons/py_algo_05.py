"""python-algo-05: Binary Trees, Tries, and Structural Invariants.

Run the worked examples, then implement the six contracts.
Complete answers belong in the reference area.
"""

from __future__ import annotations

from collections.abc import Iterable
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
    """
    Accept a Node root or None and return the number of distinct reachable nodes. Every
    reachable value must be a Python int excluding bool, and each child must be a Node or
    None. Reject cycles, repeated child object identities, malformed children and invalid
    values with ValueError. Duplicate values in different nodes remain valid. Use an
    iterative traversal and preserve the structure.
    """
    raise NotImplementedError("Implement validate_tree")


def preorder(root: Node | None) -> list[int]:
    """
    Validate the binary tree, then return values in root-left-right preorder without
    recursion or mutation. None returns an empty list. Invalid structures raise ValueError
    under validate_tree. Push children so the left branch is visited first. Do not infer
    traversal order by sorting payload values.
    """
    raise NotImplementedError("Implement preorder")


def tree_height(root: Node | None) -> int:
    """
    Validate the binary tree and return its height measured in nodes: None has height 0, a
    leaf has height 1. Use an iterative traversal carrying depth, preserve the tree, and
    reject invalid structures with ValueError. A long one-child chain must work without
    increasing Python's recursion limit.
    """
    raise NotImplementedError("Implement tree_height")


def is_strict_bst(root: Node | None) -> bool:
    """
    First validate tree ownership, then return whether every left descendant is strictly
    smaller and every right descendant strictly larger than its ancestor. Reject malformed
    structures with ValueError, but return False for ordering violations or duplicate
    values. Empty trees return True. Use an iterative bound-carrying traversal and preserve
    input.
    """
    raise NotImplementedError("Implement is_strict_bst")


def build_trie(words: Iterable[str]) -> TrieNode:
    """
    Build a fresh TrieNode tree from a one-pass iterable of Python strings. Each edge key is
    one Unicode code point; terminal marks complete words. Duplicate words are idempotent,
    empty string sets the root terminal marker, and empty input returns an empty nonterminal
    root. Reject nonstring words with ValueError. Do not normalize case or Unicode and do
    not retain the input iterable.
    """
    raise NotImplementedError("Implement build_trie")


def prefix_words(root: TrieNode, prefix: str, limit: int) -> list[str]:
    """
    Validate the complete TrieNode structure: child keys must be single-code-point strings,
    terminal flags bool, and node identities unshared and acyclic. Require string prefix and
    nonnegative integer limit excluding bool. Return at most limit stored words beginning
    with prefix in Python lexicographic order, including prefix itself when terminal.
    Missing prefixes and zero limit return []; zero still validates. Preserve the trie.
    """
    raise NotImplementedError("Implement prefix_words")


def worked_examples() -> None:
    # Distinct objects may carry the same payload.
    shared = {"value": 4, "left": None, "right": None}
    aliases = {"value": 9, "left": shared, "right": shared}
    distinct = {"value": 9, "left": dict(shared), "right": dict(shared)}
    assert aliases["left"] is aliases["right"]
    assert distinct["left"] == distinct["right"]
    assert distinct["left"] is not distinct["right"]
    shared["value"] = 7
    assert aliases["right"]["value"] == 7
    assert distinct["right"]["value"] == 4
    print("Aliased branches change together; equal copied leaves are independent.")

    import unicodedata

    words = ["car", "cart", "cat", "café", "cafe\u0301", "car"]
    code_point_matches = sorted({word for word in words if word.startswith("caf")})
    assert code_point_matches == ["cafe\u0301", "café"]
    assert len("é") == 1 and len("e\u0301") == 2
    normalized = {unicodedata.normalize("NFC", word) for word in words}
    assert len(normalized) == 4
    assert "ca" not in words and "car" in words
    print("Unnormalized prefixes:", [repr(word) for word in code_point_matches])


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement all six contracts and record boundary evidence.")

# Exercise 1: Validate object ownership before traversal
# Contract: validate_tree
# Prompt: Accept a Node root or None and return the number of distinct reachable nodes. Every
# reachable value must be a Python int excluding bool, and each child must be a Node or None.
# Reject cycles, repeated child object identities, malformed children and invalid values with
# ValueError. Duplicate values in different nodes remain valid. Use an iterative traversal and
# preserve the structure.
# Expected: None returns 0; Node(2, Node(2)) returns 2. Referencing the same child from both
# branches raises ValueError, as does a node pointing to itself.

# Exercise 2: Traverse with an explicit stack
# Contract: preorder
# Prompt: Validate the binary tree, then return values in root-left-right preorder without
# recursion or mutation. None returns an empty list. Invalid structures raise ValueError under
# validate_tree. Push children so the left branch is visited first. Do not infer traversal order
# by sorting payload values.
# Expected: Node(8, Node(3, Node(1), Node(6)), Node(10)) yields [8, 3, 1, 6, 10]. Equal-valued
# nodes still contribute separate output positions.

# Exercise 3: Define height and handle deep chains
# Contract: tree_height
# Prompt: Validate the binary tree and return its height measured in nodes: None has height 0, a
# leaf has height 1. Use an iterative traversal carrying depth, preserve the tree, and reject
# invalid structures with ValueError. A long one-child chain must work without increasing Python's
# recursion limit.
# Expected: A chain of 2500 nodes has height 2500. A root with two leaf children has height 2,
# regardless of payload values.

# Exercise 4: Enforce ancestor bounds and a duplicate policy
# Contract: is_strict_bst
# Prompt: First validate tree ownership, then return whether every left descendant is strictly
# smaller and every right descendant strictly larger than its ancestor. Reject malformed
# structures with ValueError, but return False for ordering violations or duplicate values. Empty
# trees return True. Use an iterative bound-carrying traversal and preserve input.
# Expected: A root 8 with left child 3 whose right child is 9 is invalid, even though 9 exceeds
# its immediate parent 3. A separate node equal to the root also makes strict ordering False.

# Exercise 5: Represent prefixes and whole words separately
# Contract: build_trie
# Prompt: Build a fresh TrieNode tree from a one-pass iterable of Python strings. Each edge key is
# one Unicode code point; terminal marks complete words. Duplicate words are idempotent, empty
# string sets the root terminal marker, and empty input returns an empty nonterminal root. Reject
# nonstring words with ValueError. Do not normalize case or Unicode and do not retain the input
# iterable.
# Expected: Words ["", "car", "cat", "car"] share the ca prefix and store car once. The prefix ca
# is not itself a word unless explicitly inserted. Two calls produce independent nodes.

# Exercise 6: Bound a deterministic prefix query
# Contract: prefix_words
# Prompt: Validate the complete TrieNode structure: child keys must be single-code-point strings,
# terminal flags bool, and node identities unshared and acyclic. Require string prefix and
# nonnegative integer limit excluding bool. Return at most limit stored words beginning with
# prefix in Python lexicographic order, including prefix itself when terminal. Missing prefixes
# and zero limit return []; zero still validates. Preserve the trie.
# Expected: For ["", "car", "cat", "café", "Cafe"], prefix ca returns ["café", "car", "cat"].
# Empty prefix with limit 2 returns ["", "Cafe"]. Unicode normalization and locale collation are
# outside this contract.
