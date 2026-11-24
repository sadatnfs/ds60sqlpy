# web-038: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-038.md`.

## Exercise 1: Explain why valid JSON can still be invalid application input.

**Expected answer:** It may contain the wrong structure, types, ranges or required fields.

**Approach:** Separate syntax from meaning: decoding proves the text is JSON, while field checks prove it has the required keys, types and ranges.

**Why:** json_decode only checks syntax, so types, ranges and required fields still need validation.

**Plausible wrong approach:** Accepting any successfully decoded value fails because {"minutes":"thirty"} is valid JSON with the wrong field type.

**How to verify:** That input decodes without error but is rejected by the `is_int` field check with a clear message. A record with `minutes` set to 30 passes the same check and continues to the next step.

## Exercise 2: Add a bounded decoding depth and explicit parse errors.

**Expected evidence:** Malformed or too-deep input produces an intentional failure.

**Approach:** Pass a depth of 32 and `JSON_THROW_ON_ERROR`, and catch `JsonException` where the input arrives.

**Why:** The depth limit bounds nesting, and the flag turns malformed input into a JsonException.

**Plausible wrong approach:** Using the default depth with no flag fails because malformed input returns null, which looks the same as valid null.

**How to verify:** Malformed text and an input nested deeper than the limit both reach the catch block with messages.

## Exercise 3: Parse a small study record and round-trip it through a temporary stream.

**Expected evidence:** The field contract passes and the returned bytes match the encoded value.

**Approach:** Decode, validate the record, encode it again, write it to `php://temp`, rewind, read it back and compare the strings.

**Why:** A temporary stream behaves like a file in memory, so the round trip shows that the written bytes equal the encoded value.

**Plausible wrong approach:** Reading immediately after `fwrite` fails because the stream cursor sits at the end, so the read returns an empty string.

**How to verify:** The value read after `rewind` is identical to the encoded string, and the field contract still passes.

## Exercise 4: Diagnose an empty read caused by the stream cursor position.

**Expected answer:** Rewind before reading from the beginning.

**Approach:** Check where the cursor is with `ftell` after writing, then call `rewind` before reading from the start.

**Why:** After writing, the cursor sits at the end of the stream, so a read returns nothing until rewind moves it back.

**Plausible wrong approach:** Reopening `php://temp` to read fails because each open creates a new empty stream, not the one you wrote.

**How to verify:** `ftell` reports 5 after writing notes and 0 after `rewind`, and the read returns notes.

## Exercise 5: Reject an unexpected field type and an oversized input string.

**Expected evidence:** The program checks both byte budget and data contract before use.

**Approach:** Check `strlen($input)` against a byte limit before decoding, then check the decoded field type with `is_int`.

**Why:** A byte budget limits work before parsing, and the field check rejects data that parses but breaks the contract.

**Plausible wrong approach:** Decoding first and measuring later fails because the oversized input has already used memory and processing time.

**How to verify:** An input over the limit is rejected before `json_decode` runs, and a string `minutes` value is rejected after.

## Exercise 6: Explain why user-controlled paths need an ownership policy.

**Expected answer:** A path can escape the intended data area or expose unrelated files; identifiers should map through a reviewed boundary.

**Approach:** Map a short identifier through a reviewed allowlist to a file inside one data directory, never using the raw input as a path.

**Why:** Paths from users can traverse outside the data area, so the program should map identifiers to files it owns.

**Plausible wrong approach:** Joining user text onto a base directory fails because ../ segments can reach files outside the intended folder.

**How to verify:** An identifier of ../secrets is rejected, while a listed identifier resolves to a file inside the data directory. Logging the resolved path with `realpath` shows it still begins with the data directory.

## Reference comparison

Open `courses/web-development/solutions/web-038_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
