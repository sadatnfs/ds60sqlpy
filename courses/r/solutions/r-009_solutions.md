# r-009: reference reasoning

Use the [complete reference](r-009_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The one-element list and the numeric measurement vector are different objects. Exact nested names retain the unit contract.

Single-bracket replacement retains the field with a NULL value; dollar replacement by NULL deletes the field.

## Explained practice

### Exercise 1

Predict is.list(x[1]) for a list x.

It is TRUE.

**Approach:** Apply single brackets to the list and test the class of the result.

**Why it holds here:** Single brackets select a sub-list. `record[1]` is a list holding one element named id, not the string "A" itself.

**Tempting mistake:** Expecting the contained value, as `record[[1]]` would return. Code that then calls `nchar()` or `toupper()` on the result gets a list method or an error instead of text handling.

**Verify:** The reference asserts `is.list(record[1])`, and `length(record[1])` returns 1.

### Exercise 2

Extract the first number from a values field.

Use record[["values"]][[1]].

**Approach:** Extract in two stages: `record[["values"]]` gives the numeric vector, then `[[1]]` gives its first element.

**Why it holds here:** The values field holds 2 and 4, so the first number is 2. Each stage has one clear job.

**Tempting mistake:** Writing `record["values"][[1]]`. The first step keeps the list wrapper, so `[[1]]` unwraps it and returns the whole vector 2, 4 instead of a single number.

**Verify:** The reference check `record[["values"]][[1]] == 2` passes and the result has length 1.

### Exercise 3

Validate required id and values fields.

Require both names, one character ID and a numeric values vector.

**Approach:** Check that both names exist, then check that id is one character string and values is numeric.

**Why it holds here:** Testing names first makes a missing field fail with a clear message. The type checks then confirm the starter's id "A" is a single string and values 2, 4 are numbers.

**Tempting mistake:** Only testing `!is.null(record$id)`. That passes for an id of 7 or of c("A", "B"), neither of which identifies one record.

**Verify:** On the starter record every check passes; setting `record$id <- 7` makes the stopifnot report `is.character(record$id) is not TRUE`.

### Exercise 4

Diagnose an accidental one-element list passed to mean.

Use [[ to obtain the numeric field.

**Approach:** Replace the single-bracket argument with `record[["values"]]` so mean receives the numeric vector.

**Why it holds here:** `record["values"]` is a list containing the vector. mean does not look inside lists, so it cannot average 2 and 4 from it.

**Tempting mistake:** Calling `mean(record["values"])`. It returns NA with a warning that the argument is not numeric or logical, and a script that ignores warnings carries the NA forward.

**Verify:** `mean(record[["values"]])` returns 3, which the reference asserts.

### Exercise 5

Retain an explicitly NULL note field.

Use record["note"] <- list(NULL).

**Approach:** Assign a list containing NULL through single brackets: `record["note"] <- list(NULL)`.

**Why it holds here:** Single-bracket replacement sets list elements from the list on the right, so the note element is created and holds NULL. The record now has three fields.

**Tempting mistake:** Writing `record$note <- NULL`. Assigning NULL with the dollar or double-bracket form removes a field; here note does not exist yet, so nothing is added at all.

**Verify:** `"note" %in% names(record)` returns TRUE, `is.null(record$note)` is TRUE, and `length(record)` returns 3.

### Exercise 6

Explain a risk of unlist on a mixed record.

A text ID can coerce numeric measurements to character and erase field structure.

**Approach:** Keep mixed records as lists and extract each field with its own type; flatten only fields that share one type.

**Why it holds here:** The id is text and values are numbers. `unlist()` needs a common type, so it converts everything to character, as Example 3 shows.

**Tempting mistake:** Flattening and then calling `as.numeric()` to recover the numbers. The id becomes NA with a coercion warning, so one field is destroyed to repair another.

**Verify:** The reference asserts `is.character(unlist(record[c("id", "values")]))`, and the flattened result has length 3 from two fields.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
