# Binary Trees, Tries, and Structural Invariants

**Stable ID:** `python-algo-05`. Allow about 150 minutes for reading,
tracing and independent implementation. This estimate is not a deadline.

## How to run this lesson

Run `./classroom` from the repository root and choose **Python** in the shared
`/classroom` directory. Select this unit, read its Python capability notice,
and open the saved coding pad. Windows learners use the same launcher in
WSL 2. Docker supplies the prepared Python Core environment and the required
standard-library modules; no extra package, dataset or service is needed.
Paste the complete [learner script](../lessons/py_algo_05.py), save and Run.
The two worked examples print their observations. The six task functions
remain unimplemented and are not called by the opening demonstrations.

Every browser Run starts a fresh process. Include imports, fixtures and your
checks together, and save the source that reproduces an observation. The
learning volume retains code, notes and results; it does not retain live tree
objects, heap contents or generator state between processes. A successful
opening demonstration is evidence for those examples, not completion of the
six independent implementations.

An optional separately prepared contributor environment can run
`uv run --no-sync python python/professional/lessons/py_algo_05.py`
from the repository root. See [contributor setup](../../../CONTRIBUTING.md)
for that route and the [classroom guide](../../../docs/classroom-experience.md)
for browser persistence. The host checkout and interpreter do not read the
browser's Docker learning volume. All inputs in this lesson are original,
tiny offline fixtures.

## Level and prerequisites

- **Level:** Advanced Python algorithm practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-12`, [classes and dataclasses](../../ds-60day/companion-guides/day12_oop_dataclasses.md).
- **Direct prerequisite:** `python-algo-03`, [graphs, shortest paths and dynamic programming](py_algo_03.md).
- **Artifacts:** [learner](../lessons/py_algo_05.py), [explained answers](../solutions/py_algo_05_solutions.md), [executable reference](../solutions/py_algo_05_solution.py).

## Learning objectives

Distinguish equal payloads from shared object ownership before traversing a
binary tree. Compute preorder and node-count height with an explicit frontier,
then carry ancestor bounds through a strict BST check. Represent complete words
and prefixes separately in a trie, and explain the exact Unicode and validation
costs behind a bounded query.

## Starting point and observable outcome

This unit is `python-algo-05`. Complete `python-12` and `python-algo-03` first. You should be comfortable defining a small Python class, following object references and traversing a graph with an explicit frontier. Open the unit in the Docker classroom's prepared Python Core environment and run the learner script. All examples use the standard library, tiny offline fixtures and a fresh process; no package or service setup is required.

Your outcome is a set of operations that first establish which structure they are allowed to traverse. You will distinguish duplicate values from duplicated object ownership, calculate an explicit height convention, enforce inherited ordering constraints, and search word prefixes without confusing a prefix with a stored word. A passing numerical answer on one neat tree is insufficient evidence: include a malformed structure, an empty case and a changed ordering condition.

## Vocabulary and concepts

- **Owned tree:** A rooted structure in which each reachable nonroot object
  has one incoming child reference and no object is reached twice. Equal payloads
  are permitted; shared node identities and cycles violate this contract.
- **Inherited bound:** An ordering restriction passed from an ancestor to all
  descendants in a branch. A local parent-child comparison alone cannot prove
  that a descendant belongs within every ancestor's permitted interval.
- **Terminal marker:** A flag recording that a trie path is a complete stored
  word. A path can be terminal and still have children, as with `car` and `cart`.

### Node, edge, root, leaf and ownership

A **node** is an object containing a payload and references to children. An **edge** is one such reference. A **root** is the starting node; a **leaf** has no children. A binary tree permits at most two children at each node, conventionally named left and right. The names distinguish positions, not automatically smaller and larger values.

This unit uses a strict ownership definition: every reachable nonroot node appears through exactly one incoming child reference, and no path leads back to an earlier node. A shared child can form a directed acyclic graph, or DAG, even when there is no cycle. That is a useful structure for other applications, but it is not a valid input to these tree operations. Applying a tree algorithm to a DAG can double-count shared work, and applying it to a cycle can fail to terminate.

Payload equality is independent of identity. Two separate nodes can both hold the integer 4 and still be distinct valid tree nodes. One node referenced from both branches violates ownership even if every numeric value in the structure looks reasonable. Validation therefore tracks object identities with `id(node)`, rather than putting payload values into a seen set.

## Syntax anatomy and the provided scaffolds

The learner file supplies `Node` and `TrieNode` dataclasses as representations, leaving all six operation contracts unimplemented. `Node` has `value`, `left` and `right` fields. `None` means an absent child or an empty tree. The `eq=False` declaration avoids recursively comparing whole node structures when identity is the intended distinction.

A `TrieNode` has a child dictionary and a `terminal` flag. `field(default_factory=dict)` creates a separate dictionary for each instance. A shared mutable dictionary would make independent nodes accidentally share branches. The scaffolds are intentionally inspectable so you can test ownership; callers must still respect the operations' declared invariants.

Python's `is` compares identity, while `==` compares equality as defined by the objects. These are different questions. Do not try to prove tree ownership by checking whether two leaf payloads compare equal, and do not modify a bad link to make a validation test pass. The original structure is the evidence being diagnosed.

## Worked example: equal leaves and aliased leaves differ

Predict which right leaf changes after the mutation. This complete example uses dictionaries so the ownership mechanism is visible before introducing tree traversal code.

```python
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
```

Both copied leaves initially compare equal by contents, but they are different objects. Updating `shared` changes both references in `aliases`; it leaves the copied dictionaries alone. In a graph, that sharing can be intentional. In this lesson's binary tree, it must be rejected before counting or calculating height.

Now replace `shared["left"]` with `shared` itself. The reference graph contains a cycle rather than merely shared ownership. A validator that only checks the immediate left and right children against one another misses this case. A traversal-wide identity set detects both forms of repeated reachability without recursion.

## Traversal order and height conventions

Preorder means visiting the root, then the left subtree, then the right subtree. With a last-in-first-out stack, push the right child before the left. Sorting the output numbers cannot recover preorder because preorder encodes topology, not numeric order. Two trees can hold the same bag of values yet have different traversals.

Height is measured in nodes here. The empty tree has height zero and a leaf has height one. In recurrence form,

\[
h(\varnothing)=0,\qquad h(v)=1+\max(h(v_{\mathrm{left}}),h(v_{\mathrm{right}})).
\]

The reference implements that idea iteratively by carrying a depth with each pending node. A chain of 2500 nodes should work without changing the interpreter's recursion limit. A balanced tree often has logarithmic height, while a chain has height equal to its node count. Binary branching alone does not imply balance.

Validation uses a seen set with one identity per reachable node. Preorder additionally allocates its output list. Although a depth-first traversal frontier can be bounded by height, the complete public operation is not advertised as using only height-sized memory because validation is included. Complexity statements must describe the whole contract being called.

## Binary-search ordering is an inherited constraint

A binary search tree, or BST, adds ordering to the shape. Under this unit's strict policy, every value in a left subtree is smaller than the ancestor and every value in a right subtree is larger. Duplicates are structurally legal tree values but make a strict BST test return False.

Consider root 8, left child 3, and 3's right child 9. Comparing only parents with immediate children accepts both local relations. However, 9 is still inside the left subtree of 8 and violates the ancestor bound. Carry an open interval \((L,U)\) down the traversal: moving left tightens the upper bound, while moving right tightens the lower bound. A missing bound can use `None` because node values are integers.

A malformed graph raises an exception. A well-formed tree with wrong ordering returns False. The validating pass happens first, ensuring an early ordering failure cannot conceal an unrelated cycle. This distinction lets callers diagnose data integrity separately from an ordinary negative search-tree property.

## Worked example: prefixes use code points, not appearance

A trie follows one edge for each code point. Before constructing one, use this complete list-based example to predict its exact word semantics.

```python
import unicodedata

words = ["car", "cart", "cat", "café", "cafe\u0301", "car"]
code_point_matches = sorted({word for word in words if word.startswith("caf")})
assert code_point_matches == ["cafe\u0301", "café"]
assert len("é") == 1 and len("e\u0301") == 2
normalized = {unicodedata.normalize("NFC", word) for word in words}
assert len(normalized) == 4
assert "ca" not in words and "car" in words
print("Unnormalized prefixes:", [repr(word) for word in code_point_matches])
```

The two accented spellings look similar but differ in code-point sequences. The precomposed spelling has one final code point; the decomposed spelling uses a base letter and combining accent. This unit does not normalize them, ignore case or apply locale collation. Its deterministic ordering is Python's lexicographic string ordering.

If an application requires human-facing equivalence, choose and document normalization before insertion and query. Apply the same policy at both boundaries. Normalizing only the query can miss words stored under a different representation. A code-point trie is also not a grapheme-cluster editor: a visually single character can span multiple trie edges.

## Trie terminals, prefix sharing and costs

Words `car` and `cart` share the path for `car`. A terminal flag records that the shorter path is itself a whole word even though it has a child. Storing words only at leaves would lose `car`. The empty string is represented by marking the root terminal, while an empty vocabulary leaves that flag false.

Duplicate insertion is idempotent because setting an existing terminal flag again does not create a second word. Separate builder calls must produce independent trees. The constructor consumes a one-pass iterable and stores the necessary prefix nodes, not the original input collection.

The prefix query first validates the whole exposed trie, then follows the prefix and enumerates matching terminal paths in order. Its limit caps returned words, but does not remove the full validation scan or guarantee constant temporary memory. Sorting child keys and constructing output strings also have costs. A production representation could validate once and expose only safe mutations; this educational API makes structural checking observable on every query.

## Exercises

### Six exercises

Implement these functions in `python/professional/lessons/py_algo_05.py`. Use the supplied node classes, keep caller-owned links intact, and record both expected results and exceptions. Make at least one test use an asymmetric tree so traversal mistakes cannot hide.

1. **Validate object ownership before traversal: `validate_tree`.** Accept a Node root or None and return the number of distinct reachable nodes. Every reachable value must be a Python int excluding bool, and each child must be a Node or None. Reject cycles, repeated child object identities, malformed children and invalid values with ValueError. Duplicate values in different nodes remain valid. Use an iterative traversal and preserve the structure.

   **Expected:** None returns 0; Node(2, Node(2)) returns 2. Referencing the same child from both branches raises ValueError, as does a node pointing to itself.

2. **Traverse with an explicit stack: `preorder`.** Validate the binary tree, then return values in root-left-right preorder without recursion or mutation. None returns an empty list. Invalid structures raise ValueError under validate_tree. Push children so the left branch is visited first. Do not infer traversal order by sorting payload values.

   **Expected:** Node(8, Node(3, Node(1), Node(6)), Node(10)) yields [8, 3, 1, 6, 10]. Equal-valued nodes still contribute separate output positions.

3. **Define height and handle deep chains: `tree_height`.** Validate the binary tree and return its height measured in nodes: None has height 0, a leaf has height 1. Use an iterative traversal carrying depth, preserve the tree, and reject invalid structures with ValueError. A long one-child chain must work without increasing Python's recursion limit.

   **Expected:** A chain of 2500 nodes has height 2500. A root with two leaf children has height 2, regardless of payload values.

4. **Enforce ancestor bounds and a duplicate policy: `is_strict_bst`.** First validate tree ownership, then return whether every left descendant is strictly smaller and every right descendant strictly larger than its ancestor. Reject malformed structures with ValueError, but return False for ordering violations or duplicate values. Empty trees return True. Use an iterative bound-carrying traversal and preserve input.

   **Expected:** A root 8 with left child 3 whose right child is 9 is invalid, even though 9 exceeds its immediate parent 3. A separate node equal to the root also makes strict ordering False.

5. **Represent prefixes and whole words separately: `build_trie`.** Build a fresh TrieNode tree from a one-pass iterable of Python strings. Each edge key is one Unicode code point; terminal marks complete words. Duplicate words are idempotent, empty string sets the root terminal marker, and empty input returns an empty nonterminal root. Reject nonstring words with ValueError. Do not normalize case or Unicode and do not retain the input iterable.

   **Expected:** Words ["", "car", "cat", "car"] share the ca prefix and store car once. The prefix ca is not itself a word unless explicitly inserted. Two calls produce independent nodes.

6. **Bound a deterministic prefix query: `prefix_words`.** Validate the complete TrieNode structure: child keys must be single-code-point strings, terminal flags bool, and node identities unshared and acyclic. Require string prefix and nonnegative integer limit excluding bool. Return at most limit stored words beginning with prefix in Python lexicographic order, including prefix itself when terminal. Missing prefixes and zero limit return []; zero still validates. Preserve the trie.

   **Expected:** For ["", "car", "cat", "café", "Cafe"], prefix ca returns ["café", "car", "cat"]. Empty prefix with limit 2 returns ["", "Cafe"]. Unicode normalization and locale collation are outside this contract.

## Common pitfalls

### Diagnosis, applications and retrieval

If the node count is too small, check whether equal payloads were mistaken for repeated identities. If it is too large, inspect shared child references. If a traversal loops or hits recursion depth, separate structural validation from the choice of frontier. If a BST check passes the 8, 3, 9 example, inspect inherited bounds rather than adding another local comparison.

These mechanisms apply to expression trees, owned configuration structures, hierarchical indexes and dictionary prefix completion. A shared expression DAG needs a different contract from an owned tree, and a search trie needs a text policy appropriate to its application. Explain the difference before changing the implementation.

## Self-check

Without consulting the solution, describe why a duplicate value is not a cycle, why a two-node chain has height two here, and why `car` needs a terminal marker when `cart` exists. Then construct one normalization-sensitive query and state exactly which strings it should return.

## Next step

After checking all six contracts, continue to
[disjoint sets and minimum spanning forests](py_algo_06.md) when its graph and
heap prerequisites are also complete. Carry forward the distinction between
an internal representation and the property it is intended to establish.
For a text-facing application, specify normalization at both insertion and
query boundaries before reusing this trie's code-point contract.

## Official API references

See [Python dataclasses](https://docs.python.org/3.12/library/dataclasses.html) for independent mutable defaults and [Unicode normalization](https://docs.python.org/3.12/library/unicodedata.html#unicodedata.normalize) for the optional text policy illustrated above.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-05: Binary Trees, Tries, and Structural Invariants.
Read python/professional/companion-guides/py_algo_05.md and python/professional/lessons/py_algo_05.py. Direct prerequisites: python-12, python-algo-03. Keep explanations within that boundary and introduce new vocabulary at a beginner-friendly pace.
Focus on tree ownership versus DAGs, iterative traversal, height, strict BST bounds, trie terminal markers, Unicode code-point prefixes. Explain one mechanism, ask me to predict a concrete result, let me attempt it, give one hint at a time, then review my output, invariant, memory or exception evidence. Ask me to retrieve the explanation in my own words. Do not read solutions/ until I ask or have made an honest attempt.
For retrieval, ask me to distinguish equal node values from aliased children, trace the inherited bound in the 8, 3, 9 counterexample, and explain why a stored prefix needs a terminal flag. Require my own words and a changed boundary fixture.
Use only the Docker classroom's prepared Python Core environment, standard-library code and tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database writes, downloads or external services; do not execute live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a counterexample to an incorrect algorithm and the actual retained-state cost.
```
