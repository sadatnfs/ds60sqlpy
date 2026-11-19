# web-038: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-038.md`.

## Exercise 1: Explain why valid JSON can still be invalid application input.

**Expected answer:** It may contain the wrong structure, types, ranges or required fields.

**Why:** json_decode only checks syntax, so types, ranges and required fields still need validation.

## Exercise 2: Add a bounded decoding depth and explicit parse errors.

**Expected evidence:** Malformed or too-deep input produces an intentional failure.

**Why:** The depth limit bounds nesting, and the flag turns malformed input into a JsonException.

## Exercise 3: Parse a small study record and round-trip it through a temporary stream.

**Expected evidence:** The field contract passes and the returned bytes match the encoded value.

**Why:** A temporary stream behaves like a file in memory, so the round trip shows that the written bytes equal the encoded value.

## Exercise 4: Diagnose an empty read caused by the stream cursor position.

**Expected answer:** Rewind before reading from the beginning.

**Why:** After writing, the cursor sits at the end of the stream, so a read returns nothing until rewind moves it back.

## Exercise 5: Reject an unexpected field type and an oversized input string.

**Expected evidence:** The program checks both byte budget and data contract before use.

**Why:** A byte budget limits work before parsing, and the field check rejects data that parses but breaks the contract.

## Exercise 6: Explain why user-controlled paths need an ownership policy.

**Expected answer:** A path can escape the intended data area or expose unrelated files; identifiers should map through a reviewed boundary.

**Why:** Paths from users can traverse outside the data area, so the program should map identifiers to files it owns.

## Reference comparison

Open `courses/web-development/solutions/web-038_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
