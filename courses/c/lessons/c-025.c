#include <stdio.h>

int main(void) {
  /* Exercise 1: Traverse a small tree: change one input
     Copy worked example 1, the "traverse a small tree" case, into a scratch pad
     and change `struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},`
     to `struct Tree left = {2, NULL, NULL}, right = {3, NULL, NULL},`. Before
     running, predict which CHECK fails and which value it sees in place of the
     worked result (the total is 6); then run it and restore the original line.
     Expected: With `struct Tree left = {2, NULL, NULL}, right = {3, NULL,
     NULL},` the run stops with `Check failed` at the CHECK on `tree_sum(&root)
     == 6`, because the "traverse a small tree" case no longer shows that the
     total is 6. Restoring `struct Tree left = {1, NULL, NULL}, right = {3,
     NULL, NULL},` brings that observation back. */

  /* Exercise 2: Handle an empty tree: diagnose an edited check
     A careless edit changed the CHECK in worked example 2, the "handle an empty
     tree" case, so that it reads `CHECK(tree_sum(NULL) != 0);`. Run the example
     with that line, explain why the edited CHECK now fails even though the
     program state still means the result is zero, and restore it. Expected:
     Before the repair the run stops with `Check failed` at the CHECK on
     `tree_sum(NULL) == 0`. Once the line reads `CHECK(tree_sum(NULL) == 0);`
     again, the "handle an empty tree" case again shows that the result is zero.
   */

  /* Exercise 3: Measure structural depth
     Measure the root and two children.
     Expected: The depth is 2. */

  /* Exercise 4: Find an existing value
     Search the tree for 3 with sufficient budget.
     Expected: The value is found. */

  /* Exercise 5: Respect a depth limit
     Search for the child value with only one level allowed.
     Expected: The bounded search does not descend to the child. */

  /* Exercise 6: Transfer a singleton
     Measure and sum one node containing 7.
     Expected: Depth is 1 and sum is 7. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
