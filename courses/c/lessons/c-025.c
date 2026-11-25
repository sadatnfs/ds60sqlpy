#include <stdio.h>

int main(void) {
  /* Exercise 1: Traverse a small tree: change one input
     In worked example 1, change `struct Tree left = {1, NULL, NULL}, right =
     {3, NULL, NULL},` to `struct Tree left = {2, NULL, NULL}, right = {3, NULL,
     NULL},`. Predict which value the CHECK on `tree_sum(&root) == 6` sees, then
     run and restore. Expected: `Check failed` at `tree_sum(&root) == 6`;
     restoring `struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},`
     passes again. */

  /* Exercise 2: Handle an empty tree: diagnose an edited check
     Worked example 2's CHECK now reads `CHECK(tree_sum(NULL) != 0);`. Explain
     why it fails although the result is zero, then restore it. Expected: `Check
     failed` until the CHECK reads `CHECK(tree_sum(NULL) == 0);` again, though
     the result is zero. */

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
