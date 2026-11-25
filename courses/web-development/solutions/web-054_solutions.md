# web-054: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-054.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Distinguish a JSON number from a numeric-looking string.

**Expected answer:** 30 and "30" have different JSON types and can affect client validation.

**Approach:** Encode `30` and `'30'` with `json_encode` and compare the output: one has no quotes and one does.

**Why:** 30 encodes as a JSON number and "30" as a string, and clients that validate types treat them differently.

**Plausible wrong approach:** Treating both as the same because they display identically fails because JavaScript `30 === '30'` is false on the client.

**How to verify:** `json_encode(['m' => 30])` prints {"m":30}, while the string version prints {"m":"30"}. Decoding both outputs with `json_decode` gives an int for the first and a string for the second.

## Exercise 2: Add a consistent error code to invalid-input responses.

**Expected evidence:** Clients can inspect a stable code without parsing human prose.

**Approach:** Add an `error.code` field such as invalid_plan next to the human message in every validation response.

**Why:** Clients can branch on a stable code, while the message can change wording or language freely.

**Plausible wrong approach:** Having clients match on the message text fails because rewording or translating the message silently breaks them.

**How to verify:** Two invalid inputs with different messages share the same code value in their decoded bodies.

## Exercise 3: Build a response model that maps success and validation failure consistently.

**Expected evidence:** Status, content type and JSON body agree with the declared contract.

**Approach:** Write one function that takes a domain result and returns status, headers and JSON body for both success and validation failure.

**Why:** A single mapping keeps success and error responses consistent with the documented contract.

**Plausible wrong approach:** Returning status 200 with an error object fails because clients that check status treat the failure as a success.

**How to verify:** The success case returns 200 and the failure returns a 4xx status such as 422, both with `Content-Type: application/json`. Decoding the failure body shows the same field keys the client already reads for success.

## Exercise 4: Diagnose an internal exception serialized directly to a public response.

**Expected answer:** Translate it at the boundary and keep sensitive details in controlled diagnostics.

**Approach:** Catch the exception at the response boundary, log its details, and return a generic error body with a stable code.

**Why:** Internal messages can reveal paths, queries or secrets, so public responses should carry only a safe code and message.

**Plausible wrong approach:** Passing `$e->getMessage()` into the response fails because messages can include file paths, SQL text or configuration values.

**How to verify:** The response body contains only the code and a short message, while the log holds the exception class.

## Exercise 5: Round-trip a Unicode label and a boolean through JSON.

**Expected evidence:** The decoded values retain their intended types and text.

**Approach:** Encode an array with a label such as Café and `true`, decode it with `json_decode(..., true)`, and compare types.

**Why:** With JSON_UNESCAPED_UNICODE the text stays readable, and json_decode returns the same string and boolean types.

**Plausible wrong approach:** Comparing the encoded strings byte for byte fails because escaping options can change the text while the data is equal.

**How to verify:** The decoded label equals the original with `===`, and `is_bool` returns true for the flag. The decoded minutes value passes `is_int`, so numbers also survive the round trip.

## Exercise 6: Explain a backward-compatible versus breaking API change.

**Expected answer:** Compatibility depends on the documented client contract, especially type and semantic changes.

**Approach:** Classify changes by what existing clients rely on: adding a field is usually safe, while renaming or retyping one is not.

**Why:** Adding an optional field is usually compatible, while removing a field or changing its type or meaning breaks clients.

**Plausible wrong approach:** Changing minutes from a number to a string and calling it compatible fails because clients doing arithmetic now get wrong results.

**How to verify:** Your examples include one additive change and one breaking change, with the client behavior each affects.

## Reference comparison

The reference decodes a success body and requires integer minutes and boolean complete, then requires a validation error to carry status 422. That catches stringly typed fields. It does not check real Content-Type or status headers on a server, so the lab is still needed for that evidence.

Open `courses/web-development/solutions/web-054_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
