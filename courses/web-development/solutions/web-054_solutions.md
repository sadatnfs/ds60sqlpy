# web-054: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-054.md`.

## Exercise 1: Distinguish a JSON number from a numeric-looking string.

**Expected answer:** 30 and "30" have different JSON types and can affect client validation.

**Why:** 30 encodes as a JSON number and "30" as a string, and clients that validate types treat them differently.

## Exercise 2: Add a consistent error code to invalid-input responses.

**Expected evidence:** Clients can inspect a stable code without parsing human prose.

**Why:** Clients can branch on a stable code, while the message can change wording or language freely.

## Exercise 3: Build a response model that maps success and validation failure consistently.

**Expected evidence:** Status, content type and JSON body agree with the declared contract.

**Why:** A single mapping keeps success and error responses consistent with the documented contract.

## Exercise 4: Diagnose an internal exception serialized directly to a public response.

**Expected answer:** Translate it at the boundary and keep sensitive details in controlled diagnostics.

**Why:** Internal messages can reveal paths, queries or secrets, so public responses should carry only a safe code and message.

## Exercise 5: Round-trip a Unicode label and a boolean through JSON.

**Expected evidence:** The decoded values retain their intended types and text.

**Why:** With JSON_UNESCAPED_UNICODE the text stays readable, and json_decode returns the same string and boolean types.

## Exercise 6: Explain a backward-compatible versus breaking API change.

**Expected answer:** Compatibility depends on the documented client contract, especially type and semantic changes.

**Why:** Adding an optional field is usually compatible, while removing a field or changing its type or meaning breaks clients.

## Reference comparison

Open `courses/web-development/solutions/web-054_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
