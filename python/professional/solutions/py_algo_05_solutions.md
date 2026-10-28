# python-algo-05: Explained reference solutions

Compare these answers with an honest attempt at [Binary Trees, Tries, and Structural Invariants](../companion-guides/py_algo_05.md). The [standalone executable reference](py_algo_05_solution.py) includes all imports, type scaffolds, helpers and normal/boundary checks in `main()`. The snippets below use that shared context and match the six learner contracts.

## Exercise 1: Validate object ownership before traversal

**Contract: `validate_tree`.** Accept a Node root or None and return the number of distinct reachable nodes. Every reachable value must be a Python int excluding bool, and each child must be a Node or None. Reject cycles, repeated child object identities, malformed children and invalid values with ValueError. Duplicate values in different nodes remain valid. Use an iterative traversal and preserve the structure.

**Expected:** None returns 0; Node(2, Node(2)) returns 2. Referencing the same child from both branches raises ValueError, as does a node pointing to itself.

```python
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
```

Track object identities, not payload values. A shared child makes a directed acyclic graph possible, but violates this tree ownership contract even without a cycle. An iterative stack avoids recursion-depth failures on a long chain. The seen set requires linear auxiliary memory and is part of the validation cost. The function never repairs links, because silently deleting an edge would change the caller's structure.

## Exercise 2: Traverse with an explicit stack

**Contract: `preorder`.** Validate the binary tree, then return values in root-left-right preorder without recursion or mutation. None returns an empty list. Invalid structures raise ValueError under validate_tree. Push children so the left branch is visited first. Do not infer traversal order by sorting payload values.

**Expected:** Node(8, Node(3, Node(1), Node(6)), Node(10)) yields [8, 3, 1, 6, 10]. Equal-valued nodes still contribute separate output positions.

```python
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
```

A stack removes its most recently added item first. Pushing the right child before the left makes the left branch the next work item. Sorting values would erase the topology, so it cannot implement preorder. The validating pass and traversal are both linear. Although the traversal stack can be height-bounded, this public function also pays for validation and the output list.

## Exercise 3: Define height and handle deep chains

**Contract: `tree_height`.** Validate the binary tree and return its height measured in nodes: None has height 0, a leaf has height 1. Use an iterative traversal carrying depth, preserve the tree, and reject invalid structures with ValueError. A long one-child chain must work without increasing Python's recursion limit.

**Expected:** A chain of 2500 nodes has height 2500. A root with two leaf children has height 2, regardless of payload values.

```python
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
```

Height conventions differ across references, so the node-count convention must be written in the contract. Carry depth with each pending node and keep the largest visited depth. This computes a structural property rather than the maximum numeric value. An unbalanced tree may have height equal to its node count; calling a structure a binary tree does not imply logarithmic height.

## Exercise 4: Enforce ancestor bounds and a duplicate policy

**Contract: `is_strict_bst`.** First validate tree ownership, then return whether every left descendant is strictly smaller and every right descendant strictly larger than its ancestor. Reject malformed structures with ValueError, but return False for ordering violations or duplicate values. Empty trees return True. Use an iterative bound-carrying traversal and preserve input.

**Expected:** A root 8 with left child 3 whose right child is 9 is invalid, even though 9 exceeds its immediate parent 3. A separate node equal to the root also makes strict ordering False.

```python
def is_strict_bst(root: Node | None) -> bool:
    validate_tree(root)
    pending = [] if root is None else [(root, None, None)]
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
```

Immediate-child comparisons miss violations inherited from higher ancestors. Each pending node needs the open lower and upper bounds established by its path. None can represent an absent bound because payloads are integers. Structural invalidity is exceptional; ordinary non-BST ordering is a boolean result. Validation runs first so an early ordering failure cannot hide a cycle elsewhere.

## Exercise 5: Represent prefixes and whole words separately

**Contract: `build_trie`.** Build a fresh TrieNode tree from a one-pass iterable of Python strings. Each edge key is one Unicode code point; terminal marks complete words. Duplicate words are idempotent, empty string sets the root terminal marker, and empty input returns an empty nonterminal root. Reject nonstring words with ValueError. Do not normalize case or Unicode and do not retain the input iterable.

**Expected:** Words ["", "car", "cat", "car"] share the ca prefix and store car once. The prefix ca is not itself a word unless explicitly inserted. Two calls produce independent nodes.

```python
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
```

A terminal flag distinguishes a word from an internal prefix. Storing only leaves would lose words such as car when cart is also present. default_factory creates a separate child dictionary per node; a shared mutable default would corrupt ownership. Python string iteration uses code points, so composed and decomposed spellings may follow different paths even when they look alike.

## Exercise 6: Bound a deterministic prefix query

**Contract: `prefix_words`.** Validate the complete TrieNode structure: child keys must be single-code-point strings, terminal flags bool, and node identities unshared and acyclic. Require string prefix and nonnegative integer limit excluding bool. Return at most limit stored words beginning with prefix in Python lexicographic order, including prefix itself when terminal. Missing prefixes and zero limit return []; zero still validates. Preserve the trie.

**Expected:** For ["", "car", "cat", "café", "Cafe"], prefix ca returns ["café", "car", "cat"]. Empty prefix with limit 2 returns ["", "Cafe"]. Unicode normalization and locale collation are outside this contract.

```python
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
    result = []
    pending = [(node, prefix)]
    while pending and len(result) < limit:
        node, word = pending.pop()
        if node.terminal:
            result.append(word)
        for character in sorted(node.children, reverse=True):
            pending.append((node.children[character], word + character))
    return result
```

Validate before query so an exposed malformed trie cannot loop indefinitely. Descend through the prefix, then visit terminal nodes before their sorted children. Reverse push order restores ascending output under a stack. The limit caps returned words, not total validation work or all temporary string storage. A production opaque trie could validate on construction and expose a cheaper trusted query; this teaching API explicitly pays the full structural scan.

## Independent checks and limits

The reference main exercises every named contract. `tests/test_python_algorithm_modernization.py` adds independent oracles, including explicit graph reachability and exhaustive tiny spanning forests, centered rational moment calculations, sorted-prefix medians and exhaustive reservoir draw paths. Source-level contract checks are separate from semantic execution. A passing reference demonstrates tested behavior, not mastery; explain the invariant and construct a counterexample to a tempting incorrect implementation.
