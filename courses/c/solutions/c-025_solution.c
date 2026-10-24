#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void lesson_check(bool condition, const char *file, int line) {
  if (!condition) {
    fprintf(stderr, "Check failed at %s:%d\n", file, line);
    abort();
  }
}
#define CHECK(condition) lesson_check((condition), __FILE__, __LINE__)

struct Tree {
  int value;
  const struct Tree *left, *right;
};
static int tree_sum(const struct Tree *node) {
  if (node == NULL)
    return 0;
  return node->value + tree_sum(node->left) + tree_sum(node->right);
}
static size_t tree_depth(const struct Tree *node) {
  if (node == NULL)
    return 0;
  size_t a = tree_depth(node->left), b = tree_depth(node->right);
  return 1 + (a > b ? a : b);
}
static bool tree_contains(const struct Tree *node, int target, size_t budget) {
  if (node == NULL || budget == 0)
    return false;
  if (node->value == target)
    return true;
  return tree_contains(node->left, target, budget - 1) ||
         tree_contains(node->right, target, budget - 1);
}

int main(void) {
  /* Traverse a small tree */
  {
    struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
                root = {2, &left, &right};
    CHECK(tree_sum(&root) == 6);
  }

  /* Handle an empty tree */
  {
    CHECK(tree_sum(NULL) == 0);
  }

  /* Measure structural depth */
  {
    struct Tree left = {1, NULL, NULL}, right = {3, NULL, NULL},
                root = {2, &left, &right};
    CHECK(tree_depth(&root) == 2);
  }

  /* Find an existing value */
  {
    struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
    CHECK(tree_contains(&root, 3, 2));
  }

  /* Respect a depth limit */
  {
    struct Tree leaf = {3, NULL, NULL}, root = {2, NULL, &leaf};
    CHECK(!tree_contains(&root, 3, 1));
  }

  /* Transfer a singleton */
  {
    struct Tree root = {7, NULL, NULL};
    CHECK(tree_depth(&root) == 1 && tree_sum(&root) == 7);
  }
  puts("All lesson checks passed.");
  return 0;
}
