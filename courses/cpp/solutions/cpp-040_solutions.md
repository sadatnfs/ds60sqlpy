# cpp-040: explanations and reference observations

The [executable reference](cpp-040_solution.cpp) accepts `"0"` and a 16-character name and rejects the backslash in `a\b` and the uppercase `Upper`. The explanations cover allow-lists, length limits and the row budget in Exercise 6. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

Hardening means enforcing explicit bounds before processing untrusted-shaped input. Path validation distinguishes a user-supplied identifier from a filesystem path. Resource limits cap input length, row count and execution work. A parser may be memory-safe yet still accept dangerous locations or consume unreasonable resources.

## Detailed reasoning

The allowed identifier grammar avoids interpreting input as a path at all. batch_7 is a name; ../secret and a/b contain characters that cannot enter this narrow namespace. This does not solve the general problem of safe filesystem containment with symlinks and races. Keep that limitation explicit. Row and byte limits bound work before parsing, and publication should occur only after the accepted/rejected accounting meets the declared policy.

<!-- depth:start -->
## Validation, budgets and safe publication

Input validation is a translation from untrusted bytes into a deliberately smaller trusted domain. The identifier grammar here accepts a bounded name such as batch_7 and rejects separators or parent traversal syntax. It avoids interpreting arbitrary input as a filesystem path. That is a simpler and more reviewable contract than attempting to sanitize every possible path string after the fact.

A narrow identifier check is not a general filesystem containment proof. Symlinks, races, mounts and platform path semantics can matter once a name is mapped to a real location. The lesson's safe_id helper only establishes its documented character and length policy. Actual file opening should use an owned directory and a separately reviewed path/creation contract.

Budgets belong before expensive work. Limit input bytes, record count and field length while reading, not after an unbounded file has already been loaded. A parser that rejects a million-character line only after allocating it may enforce a format rule but fail the intended resource bound. The capstone readers demonstrate incremental admission rather than merely checking final vector size.

Validation should preserve the difference between a rejected record and a failed operation. A bad identifier can be reported without publishing an output file under a guessed alternate name. A fatal read or budget failure should prevent an apparently complete report. If partial acceptance is allowed, the accepted/rejected accounting and output schema must state that policy explicitly.

A secure-looking function name is not evidence. Test exact length boundaries, empty input, allowed punctuation, slash/backslash and traversal strings as appropriate to the declared grammar. Keep the expected behavior independent of implementation details so a too-permissive mutation is caught. Do not add broad new input forms merely to make a single failing example convenient.

## Debugging the contract

If ../secret is accepted, inspect the actual allowed-character set rather than stripping one substring. If a path uses a symlink escape, the identifier helper alone is not the relevant containment control. If memory grows before a budget error, move the limit into the reading stage. If a failure still leaves a normal-looking report, repair publication semantics and exit status instead of relying on a warning line that callers may ignore.
<!-- depth:end -->

## Worked example 1

```cpp
assert(safe_id("batch_7"));
```

Expected: The seven-character identifier uses only the allowed alphabet.

## Worked example 2

```cpp
assert(!safe_id("../secret"));
```

Expected: Dot and slash violate the narrow identifier grammar.

## Exercise 1: Write the grammar

Specify accepted identifier characters and length.

**Expected:** 1 to 16 lowercase ASCII letters, digits or underscore.

**Reasoning:** A narrow contract is easier to inspect than arbitrary path sanitization.

**Verify:** Check your specification against `safe_id`: it rejects an empty string, accepts at most 16 characters and allows only `a-z`, `0-9` and `_`, so no uppercase letter, dot or slash.

## Exercise 2: Test normal input

Validate batch_7 and 0.

**Expected:** Both accepted.

**Reasoning:** An identifier may be numeric without becoming a path.

**Verify:** Assert `safe_id("batch_7")` and `safe_id("0")`; a single digit is a valid identifier under this grammar.

## Exercise 3: Reject traversal shapes

Test ../secret, a/b and a backslash-separated path.

**Expected:** All rejected before filesystem access.

**Reasoning:** Separators are outside the grammar.

**Verify:** Assert `!safe_id("../secret")`, `!safe_id("a/b")` and `!safe_id("a\\b")`, and confirm the program makes no `std::filesystem` call for a rejected name.

## Exercise 4: Repair overclaim

Explain why this is not a general symlink-safe path sandbox.

**Expected:** No claim of arbitrary path containment; scope remains identifiers.

**Reasoning:** Filesystem races and links require stronger host operations.

**Verify:** Check that your explanation says `safe_id` only validates a name, and names a case it cannot cover, such as a symbolic link inside the data directory that points elsewhere.

## Exercise 5: Enforce size

Test empty, 16-character and 17-character strings.

**Expected:** Reject, accept, reject.

**Reasoning:** Length is checked before per-character work.

**Verify:** Assert `!safe_id("")`, `safe_id(std::string(16, 'a'))` and `!safe_id(std::string(17, 'a'))`.

## Exercise 6: Transfer row budgets

Set max 100 rows and 256 bytes per row before parsing a file.

**Expected:** Oversized input rejected with counts and no partial publication.

**Reasoning:** Input limits and output publication must form one contract.

**Verify:** Feed 101 short rows, then a single 257-byte row, and confirm each run reports the limit and count it hit and writes no output file.
