# r-005: reference reasoning

Use the [complete reference](r-005_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The requested output order is C, A, A, and duplication is preserved. This is positional extraction, not a unique-key set operation.

The first output preserves an unknown selected position. The second explicitly restricts selection to known TRUE predicates.

The reference catches the deliberately invalid mixed index so the remaining assertions can still run. That error-handling helper is explained in r-015. The selection mechanism does not depend on knowing the handler yet: positive positions retain, negative positions exclude, and those policies cannot be mixed in the illustrated index.

## Explained practice

### Exercise 1

Predict x[c(2,2,1)] for x=c(4,8).

The result is 8,8,4.

**Approach:** Read the index vector from left to right; each entry names one position to copy into the result.

**Why it holds here:** In c(4, 8), position 2 holds 8 and position 1 holds 4. The index asks for 2, 2, 1, so the output is 8, 8, 4, and its length equals the index length of three.

**Tempting mistake:** Expecting a set-like answer such as 8, 4 with the repeat removed, or a sorted 4, 8. Indexing never deduplicates or reorders on its own.

**Verify:** The reference asserts `identical(c(4, 8)[c(2, 2, 1)], c(8, 8, 4))`, and `length()` of the result returns 3.

### Exercise 2

Exclude the middle entry of c(2,4,6).

The result is 2,6.

**Approach:** Use a negative position: `c(2, 4, 6)[-2]` excludes the second entry and keeps the rest in order.

**Why it holds here:** Position 2 holds 4, so the remaining values are 2 and 6. Exclusion by position does not depend on what the values are.

**Tempting mistake:** Filtering by value with `x[x != 4]` happens to work here but would drop every 4 if the value repeated. Writing `x[-4]`, confusing the value with a position, is worse: an out-of-range negative index is ignored, so all three values come back with no error.

**Verify:** `print(c(2, 4, 6)[-2])` shows `[1] 2 6`, a result of length 2.

### Exercise 3

Select and update a validated named value.

With unique names A, B, updating B changes only that entry.

**Approach:** Validate first, then assign: check `!anyDuplicated(names(x))` and `key %in% names(x)`, and only then run `x[key] <- 9`.

**Why it holds here:** The names A and B are unique and B is present, so exactly one entry is replaced and the vector keeps its length of two.

**Tempting mistake:** Skipping the checks. A typo such as "b" appends a third element, as Example 3 shows. With duplicated names, `x["B"] <- 9` would change only the first match and leave the second B untouched.

**Verify:** The reference asserts `identical(unname(x), c(1, 9))`; `length(x)` returns 2 after the update.

### Exercise 4

Diagnose mixing c(1,-2) as an index.

Use one indexing policy, such as c(1,3) or -2.

**Approach:** Pick one indexing policy. To keep the first and third entries use `c(1, 3)`; to drop the second use `-2`.

**Why it holds here:** Positive positions retain and negative positions exclude, so `c(1, -2)` asks two incompatible questions at once. R stops with the message that only 0's may be mixed with negative subscripts.

**Tempting mistake:** Assuming R will keep position 1 and drop position 2, or wrapping the call in `try()` and carrying on with whatever came back. The mixed index never produces a value.

**Verify:** The reference's tryCatch returns TRUE for the mixed index, and both `c(2, 4, 6)[c(1, 3)]` and `c(2, 4, 6)[-2]` return 2 and 6.

### Exercise 5

Inspect selection with integer(0).

The output length is zero.

**Approach:** Index the vector with `integer(0)` and inspect the length and printed form of the result.

**Why it holds here:** No positions are requested, so nothing is copied. The result keeps the type and, for the named x in the reference, the names attribute, but has no elements.

**Tempting mistake:** Expecting NA or the full vector. Contrast `x[NA]`: a logical NA is recycled across every position, so it returns NA for each element instead of nothing.

**Verify:** The reference checks `length(x[integer(0)]) == 0L`, and `print()` shows `named numeric(0)`.

### Exercise 6

Explain why character names are not a validated join key.

Check uniqueness and missing names explicitly before keyed alignment.

**Approach:** Before any keyed lookup or update, test names for duplicates and for missing requested keys.

**Why it holds here:** R accepts `c(A = 1, A = 2)`, and `["A"]` returns only the first match, 1. A lookup by name therefore silently ignores the second record, which a real key column would never allow.

**Tempting mistake:** Treating names like a primary key in a table. Nothing enforces uniqueness, and a missing name returns NA rather than an error.

**Verify:** `anyDuplicated(c("A", "A"))` returns 2, the position of the first repeat, so the reference check `> 0L` is TRUE.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
