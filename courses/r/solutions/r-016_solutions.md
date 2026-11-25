# r-016: reference reasoning

Run the [complete reference](r-016_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

Normalization removes only surrounding whitespace. The four-digit contract rejects partial or mixed matches without converting the ID to a number.

Literal matching avoids regex wildcard semantics. The accented character uses multiple UTF-8 bytes while the string has four code-point characters.

## Explained practice

### Exercise 1

Predict fixed dot matching on "a.b" and "axb".

Only a.b matches.

**Approach:** Call `grepl(".", x, fixed = TRUE)` on c("a.b", "axb").

**Why it holds here:** Fixed matching looks for a literal dot. "a.b" contains one and "axb" does not, so the result is TRUE, FALSE.

**Tempting mistake:** Dropping `fixed = TRUE`. As a regex the dot matches any character, so both strings return TRUE and the check is useless. Escaping it as `\\.` also works, but fixed matching states the intent more plainly for a literal delimiter.

**Verify:** `identical(grepl(".", c("a.b", "axb"), fixed = TRUE), c(TRUE, FALSE))` returns TRUE.

### Exercise 2

Allow exactly five digits instead of four.

Use ^[0-9]{5}$.

**Approach:** Change the repetition count to five and keep both anchors: `^[0-9]{5}$`.

**Why it holds here:** The anchors tie the pattern to the whole field, so "00123" has exactly five digits and passes, while "123" is too short.

**Tempting mistake:** Removing the anchors. `[0-9]{5}` finds five digits inside "001234", so a six-digit value passes as a five-digit ID.

**Verify:** `grepl("^[0-9]{5}$", "00123")` returns TRUE and on "123" returns FALSE.

### Exercise 3

Split "A|12" on a literal pipe.

strsplit(..., fixed=TRUE) returns the two fields.

**Approach:** Split with `strsplit("A|12", "|", fixed = TRUE)` and take `[[1]]` to get a character vector.

**Why it holds here:** The pipe is meant as a literal delimiter, so fixed matching gives the two fields A and 12.

**Tempting mistake:** Splitting on the regex pipe. Example 3 shows the result is A, |, 1 and 2, four pieces with the delimiter kept as data.

**Verify:** `identical(fields, c("A", "12"))` returns TRUE.

### Exercise 4

Diagnose accepting "ID12 bad" with an unanchored digit search.

Use the intended anchored field grammar.

**Approach:** Validate with the anchored grammar `^[0-9]+$` instead of searching for digits.

**Why it holds here:** "ID12bad" contains 12 but also letters, so it is not an all-digit field and the anchored test rejects it.

**Tempting mistake:** Testing with `grepl("[0-9]+", x)`. It returns TRUE for "ID12bad", "A17" and "17x" alike, as the guide table shows.

**Verify:** `grepl("^[0-9]+$", "ID12bad")` returns FALSE.

### Exercise 5

Retain an empty trailing field deliberately.

Define and test an explicit parser policy rather than silently assuming every delimiter creates a retained empty component.

**Approach:** Write down the field policy, then append an empty field when a line ends with the delimiter, for example with `endsWith(x, "|")`.

**Why it holds here:** Under a two-field contract "A|" means A plus an empty second field, but strsplit returns only "A".

**Tempting mistake:** Assuming every row splits into two parts and reading `parts[[2]]`. For "A|" that stops with subscript out of bounds, or misaligns columns if rows of one and two pieces are bound into a table, since the shorter row is recycled or rejected depending on the binding function.

**Verify:** `identical(strsplit("A|", "|", fixed = TRUE)[[1]], "A")` returns TRUE, which is the behavior the policy corrects.

### Exercise 6

Explain a byte limit for Unicode text.

State encoding and byte/character units separately and test multibyte input.

**Approach:** Measure with `nchar(text, type = "bytes")` when the limit is in bytes, and say which unit applies.

**Why it holds here:** "café" is four characters but five UTF-8 bytes because é is stored as c3 a9.

**Tempting mistake:** Checking `nchar(text) <= 4` for a four-byte column. café passes, then overflows the column or is cut in the middle of é, leaving the lone byte c3, which is not valid UTF-8 on its own.

**Verify:** `nchar(text, type = "bytes")` returns 5 while `nchar(text)` returns 4.

## What the checks establish

The checks pin that a fixed pattern matches a literal dot only, that an anchored five-digit pattern accepts "00123" but rejects "123", that splitting "A|12" on a literal pipe gives "A" and "12", that an unanchored digit test cannot wrongly accept "ID12bad", that a trailing empty field is dropped by `strsplit()`, and that a four-character accented word occupies five bytes in UTF-8. They do not cover other normalization forms or right-to-left text, and they do not show what happens when your own input arrives in a different encoding.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
