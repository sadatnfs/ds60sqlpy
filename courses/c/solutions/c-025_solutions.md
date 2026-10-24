# c-025: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Recursion solves a problem by invoking the same mechanism on smaller subproblems. A base case stops the process, and a progress measure explains why each step approaches it. A binary tree naturally decomposes into a root and subtrees, but an unbalanced tree can have depth proportional to its node count. Recursive traversal therefore consumes stack space according to depth, not just total work. For untrusted or very large structures, impose a depth budget or use an explicit stack. This lesson uses fixed stack-allocated nodes with no cycles and no ownership ambiguity, separating traversal reasoning from allocation mechanics.

A node stores value, left and right pointers. NULL represents an empty subtree. A sum traversal combines the root value with both subtree sums. A depth function returns zero for empty and one plus the greater child depth otherwise. The bounded search checks its remaining depth before descending. General graph traversal also needs visited-state handling because a cycle is not a valid finite tree.

## Exercise 1: Traverse a small tree

Sum a root 2 with children 1 and 3.

```c
struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
            root = {2, &left, &right};
CHECK(tree_sum(&root) == 6);
```

**Expected:** The total is 6.

Each node contributes once under the acyclic tree assumption.

## Exercise 2: Handle an empty tree

Sum NULL.

```c
CHECK(tree_sum(NULL) == 0);
```

**Expected:** The result is zero.

The empty subtree contributes the additive identity and ends recursion.

## Exercise 3: Measure structural depth

Measure the root and two children.

```c
struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
            root = {2, &left, &right};
CHECK(tree_depth(&root) == 2);
```

**Expected:** The depth is 2.

Depth counts nested levels, not the three total nodes.

## Exercise 4: Find an existing value

Search the tree for 3 with sufficient budget.

```c
struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
CHECK(tree_contains(&root, 3, 2));
```

**Expected:** The value is found.

The budget permits visiting root and child. Each recursive call decreases the remaining allowance.

## Exercise 5: Respect a depth limit

Search for the child value with only one level allowed.

```c
struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
CHECK(!tree_contains(&root, 3, 1));
```

**Expected:** The bounded search does not descend to the child.

This bool API conflates not-found-within-budget and absent. A production diagnostic API should return a distinct budget-exhausted status when that distinction matters.

## Exercise 6: Transfer a singleton

Measure and sum one node containing 7.

```c
struct Tree root = {7, NULL, NULL};
CHECK(tree_depth(&root) == 1 && tree_sum(&root) == 7);
```

**Expected:** Depth is 1 and sum is 7.

The singleton verifies that both empty-child base cases combine correctly.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
