# r-016: reference reasoning

Use the [complete reference](r-016_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Normalization removes only surrounding whitespace. The four-digit contract rejects partial or mixed matches without converting the ID to a number.

Literal matching avoids regex wildcard semantics. The accented character uses multiple UTF-8 bytes while the string has four code-point characters.

## Explained practice

### Exercise 1

Predict fixed dot matching on "a.b" and "axb".

Only a.b matches.

**Expected evidence:** Only a.b matches.

### Exercise 2

Allow exactly five digits instead of four.

Use ^[0-9]{5}$.

**Expected evidence:** Use ^[0-9]{5}$.

### Exercise 3

Split "A|12" on a literal pipe.

strsplit(..., fixed=TRUE) returns the two fields.

**Expected evidence:** strsplit(..., fixed=TRUE) returns the two fields.

### Exercise 4

Diagnose accepting "ID12 bad" with an unanchored digit search.

Use the intended anchored field grammar.

**Expected evidence:** Use the intended anchored field grammar.

### Exercise 5

Retain an empty trailing field deliberately.

Define and test an explicit parser policy rather than silently assuming every delimiter creates a retained empty component.

**Expected evidence:** Define and test an explicit parser policy rather than silently assuming every delimiter creates a retained empty component.

### Exercise 6

Explain a byte limit for Unicode text.

State encoding and byte/character units separately and test multibyte input.

**Expected evidence:** State encoding and byte/character units separately and test multibyte input.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
