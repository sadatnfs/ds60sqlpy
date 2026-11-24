# c-025: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-025_solution.c`, implements all six cases, from the "traverse a small tree" case to the "transfer a singleton" case, in one `main.c`.

## Mechanism and assumptions

Recursion solves a problem by invoking the same mechanism on smaller subproblems. A base case stops the process, and a progress measure explains why each step approaches it. A binary tree naturally decomposes into a root and subtrees, but an unbalanced tree can have depth proportional to its node count. Recursive traversal therefore consumes stack space according to depth, not just total work. For untrusted or very large structures, impose a depth budget or use an explicit stack. This lesson uses fixed stack-allocated nodes with no cycles and no ownership ambiguity, separating traversal reasoning from allocation mechanics.

A node stores value, left and right pointers. NULL represents an empty subtree. A sum traversal combines the root value with both subtree sums. A depth function returns zero for empty and one plus the greater child depth otherwise. The bounded search checks its remaining depth before descending. General graph traversal also needs visited-state handling because a cycle is not a valid finite tree.

## Exercise 1: Traverse a small tree: change one input

Copy worked example 1, the "traverse a small tree" case, into a scratch pad and change `struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},` to `struct Tree left = {2, NULL, NULL}, right = {3, NULL, NULL},`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the total is 6); then run it and restore the original line.

The unchanged code is worked example 1:

```c
struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
            root = {2, &left, &right};
CHECK(tree_sum(&root) == 6);
```

**Expected:** With `struct Tree left = {2, NULL, NULL}, right = {3, NULL, NULL},` the run stops with `Check failed` at the CHECK on `tree_sum(&root) == 6`, because the "traverse a small tree" case no longer shows that the total is 6. Restoring `struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},` brings that observation back.

Each node contributes once under the acyclic tree assumption.

**Approach.** Add the three node values after the edit: root 2, left 2 and right 3 give 7.

**Why it holds here.** `root` stores the addresses `&left` and `&right`, so `tree_sum` reads the edited `left` through its pointer, and 7 is not 6.

**A plausible wrong approach.** Predicting 6 because `root` was built from copies of its children. The initializer stores pointers, not copies, so any change to `left` is visible through `root`.

**Verify.** Print `tree_sum(&root)` and see 7 with the edit and 6 after restoring `left` to 1.

## Exercise 2: Handle an empty tree: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "handle an empty tree" case, so that it reads `CHECK(tree_sum(NULL) != 0);`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means the result is zero, and restore it.

The unchanged code is worked example 2:

```c
CHECK(tree_sum(NULL) == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `tree_sum(NULL) == 0`. Once the line reads `CHECK(tree_sum(NULL) == 0);` again, the "handle an empty tree" case again shows that the result is zero.

The empty subtree contributes the additive identity and ends recursion.

**Approach.** Evaluate the base case: `tree_sum(NULL)` returns 0 immediately, so `!= 0` is false.

**Why it holds here.** An empty tree has no values, and 0 is the identity for addition, so returning 0 lets every leaf combine its two empty children without special cases.

**A plausible wrong approach.** Writing the base case at the leaves, `if (node->left == NULL && node->right == NULL) return node->value;`, without a null test. `tree_sum(NULL)` then dereferences a null pointer, and so does any node with exactly one child.

**Verify.** Run the restored CHECK and see the success line; print `tree_sum(NULL)` and see 0.

## Exercise 3: Measure structural depth

Measure the root and two children.

```c
struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
            root = {2, &left, &right};
CHECK(tree_depth(&root) == 2);
```

**Expected:** The depth is 2.

Depth counts nested levels, not the three total nodes.

**Approach.** Return 1 plus the larger child depth, with 0 for an empty subtree.

**Why it holds here.** Each leaf has depth 1 + 0, and the root takes 1 + max(1, 1), so the depth is 2 even though there are three nodes.

**A plausible wrong approach.** Adding the child depths instead of taking the maximum, `1 + a + b`. That counts nodes, so it returns 3 for this tree and grows with width rather than with nesting.

**Verify.** Print `tree_depth(&root)` and see 2; the summing variant prints 3.

## Exercise 4: Find an existing value

Search the tree for 3 with sufficient budget.

```c
struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
CHECK(tree_contains(&root, 3, 2));
```

**Expected:** The value is found.

The budget permits visiting root and child. Each recursive call decreases the remaining allowance.

**Approach.** Give a budget of 2: the root uses 1 and the call on the right child receives 1, enough to compare the leaf.

**Why it holds here.** The leaf's value is 3, so it returns true before the budget reaches 0, and `||` passes that result up through the root.

**A plausible wrong approach.** Treating the budget as a count of edges and passing 1. The budget counts nodes on the path including the root, so a budget of 1 stops before the child and reports false.

**Verify.** Print `tree_contains(&root, 3, 2)` and `tree_contains(&root, 3, 1)` in separate statements and see 1 and 0.

## Exercise 5: Respect a depth limit

Search for the child value with only one level allowed.

```c
struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
CHECK(!tree_contains(&root, 3, 1));
```

**Expected:** The bounded search does not descend to the child.

This bool API conflates not-found-within-budget and absent. A production diagnostic API should return a distinct budget-exhausted status when that distinction matters.

**Approach.** Check the budget before examining a node, so a budget of 1 examines only the root.

**Why it holds here.** The root holds 2, so it recurses with budget 0, and the child call returns false at once without reading the leaf.

**A plausible wrong approach.** Testing `node->value == target` before `budget == 0`. The child is then examined with budget 0 and returns true, so a search limited to one level descends anyway and this CHECK fails.

**Verify.** Compile that reordered variant and print it with budget 1 to see 1, while the lesson's helper prints 0.

## Exercise 6: Transfer a singleton

Measure and sum one node containing 7.

```c
struct Tree root = {7, NULL, NULL};
CHECK(tree_depth(&root) == 1 && tree_sum(&root) == 7);
```

**Expected:** Depth is 1 and sum is 7.

The singleton verifies that both empty-child base cases combine correctly.

**Approach.** Run both functions on one node: its two empty children supply depth 0 and sum 0.

**Why it holds here.** Depth is 1 + max(0, 0) = 1 and the sum is 7 + 0 + 0 = 7, so both base cases are exercised in a single call.

**A plausible wrong approach.** Treating the singleton as complete evidence. A leaf-only base case without a null check also returns 1 and 7 here, yet crashes on `{2, NULL, &leaf}`, so add a one-child tree to the tests.

**Verify.** Print `tree_depth` for `{2, NULL, &leaf}` and see 2 alongside the singleton's 1 and 7.

## After comparison

Write `bool tree_max(const struct Tree *node, int *out)` that returns false for an empty tree and otherwise stores the largest value. Check the singleton 7, the three-node tree (3), a tree with only negative values such as -5 over -9, and `NULL`, with `*out` unchanged on false. Explain why starting the search from 0 instead of from the root's value gives the wrong answer for the negative tree.
