# r-007: reference reasoning

Run the [complete reference](r-007_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The updated binding has a different vector value. The original labels and values remain intact.

Both names point to the same environment. This is a reference object, so the mutation is visible through either binding.

## Explained practice

### Exercise 1

Predict x after y <- x; y[1] <- 9 for a numeric vector.

x retains its earlier first value.

**Approach:** Run the assignment and the update, then inspect both vectors.

**Why it holds here:** R vectors follow copy-on-modify semantics: `y <- x` shares the data until `y[1] <- 9` changes y, at which point y gets its own copy. x still holds A = 1 and B = 2.

**Tempting mistake:** Expecting the edit to show through x because both names once referred to the same object. That is how the environment in Example 2 behaves, not an ordinary numeric vector.

**Verify:** The reference check `x[[1]] == 1` passes, and `y[[1]]` returns 9.

### Exercise 2

Remove names from a labeled vector.

The values remain while names become NULL.

**Approach:** Call `unname(x)` and compare the result with the bare values.

**Why it holds here:** `unname` removes only the names attribute. The values 1 and 2 are untouched, so the result is identical to `c(1, 2)`.

**Tempting mistake:** Writing `names(x) <- ""`. That assigns one empty name and pads the second with NA, so the object still has a names attribute and is not identical to `c(1, 2)`.

**Verify:** `is.null(names(z))` returns TRUE and `identical(z, c(1, 2))` is TRUE, as the reference asserts.

### Exercise 3

Construct a two-column shape from four numbers.

A 2 by 2 matrix retains four values.

**Approach:** Set `dim(m) <- c(2L, 2L)` on the four values from `1:4`.

**Why it holds here:** Two rows times two columns is four cells, exactly the vector length. R fills by column, so the first column is 1, 2 and the second is 3, 4.

**Tempting mistake:** Requesting `c(3L, 2L)` fails because six cells do not match four values. Expecting row filling, with 1 and 2 across the top row, misreads every later position.

**Verify:** The reference checks `identical(dim(m), c(2L, 2L))`, and `m[1, 2]` returns 3.

### Exercise 4

Diagnose a shared environment counter changing through another name.

Use a fresh environment when independent state is required.

**Approach:** Recognize that `alias <- e` gives a second name to one environment, then create a separate `new.env()` when independent state is needed.

**Why it holds here:** An environment is a reference object. Setting `alias$count <- 3` changes the only count that exists, so `e$count` becomes 3 as well.

**Tempting mistake:** Expecting `alias <- e` to copy the way `y <- x` copied a vector, and then debugging an unexpected count somewhere else in the script.

**Verify:** In the reference, `e$count` returns 3 after the alias update, and `identical(e, alias)` is TRUE.

### Exercise 5

Test exact equality of c(A=1) and 1.

identical is FALSE because one object is named.

**Approach:** Use `identical()` for exact object equality and compare the attributes as well as the values.

**Why it holds here:** `c(A = 1)` carries a names attribute that 1 lacks, so the two objects differ even though their single value matches.

**Tempting mistake:** Concluding that the values differ, or using `==` where identity was required. `c(A = 1) == 1` returns TRUE with the name A attached, hiding the metadata difference.

**Verify:** `attributes(c(A = 1))` shows a `$names` entry, while `attributes(1)` returns NULL.

### Exercise 6

State a function return contract including metadata.

Specify and test names, dimensions and class that downstream code relies on.

**Approach:** Write the contract as explicit checks on names, dimensions and class, not only on values.

**Why it holds here:** In this lesson the names A and B carry record identity, and Example 3 shows how a single-column selection can drop dim without changing any value.

**Tempting mistake:** Testing only `all(result == c(1, 2))`. That passes after `unname()` or `as.numeric()` has stripped the labels a caller relies on.

**Verify:** The reference asserts `identical(names(x), c("A", "B"))`, a test that fails as soon as the labels change.

## What the checks establish

The assertions confirm that changing a copy leaves the original first element at 1, that `unname()` removes names but keeps the values 1 and 2, that a `dim` attribute turns four numbers into a 2 by 2 shape, that an environment counter reaches 3 through shared mutation, and that `c(A = 1)` is not identical to 1 because names are part of the value. They cannot detect attributes lost in steps you add later.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
