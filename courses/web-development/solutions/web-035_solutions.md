# web-035: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-035.md`.

## Exercise 1: Explain how a list differs from a keyed record.

**Expected answer:** A list models ordered values; a record's named keys identify fields.

**Why:** A list uses consecutive integer positions, while a record's string keys name its fields.

## Exercise 2: Add a second validated study row.

**Expected evidence:** Every row has the declared subject and integer-minutes fields.

**Why:** Records with the same keys and types can be processed by one function without special cases.

## Exercise 3: Filter and summarize study records without changing the originals.

**Expected evidence:** The derived list contains only qualifying rows and retains consecutive indices.

**Why:** array_filter returns a new array, and array_values renumbers it into a list.

## Exercise 4: Diagnose JSON output changing from an array to an object shape.

**Expected answer:** Inspect numeric key gaps after filtering and reindex when the contract is a list.

**Why:** array_filter preserves keys, so gaps such as 0 and 2 make json_encode produce an object instead of a list.

## Exercise 5: Test an empty result and a missing required field.

**Expected evidence:** Empty lists are valid where declared; malformed records are rejected explicitly.

**Why:** An empty list is a valid result, while a malformed record must be rejected before it is used.

## Exercise 6: Explain the risk of a lingering foreach reference.

**Expected answer:** A reference variable can still alias the last element and cause later assignments to mutate it.

**Why:** After a by-reference loop, `$item` still points at the last element, so a later assignment overwrites it; `unset($item)` breaks the reference.

## Reference comparison

Open `courses/web-development/solutions/web-035_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
