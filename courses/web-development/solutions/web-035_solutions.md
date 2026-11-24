# web-035: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-035.md`.

## Exercise 1: Explain how a list differs from a keyed record.

**Expected answer:** A list models ordered values; a record's named keys identify fields.

**Approach:** Describe a list as positions 0, 1, 2 holding values of one kind, and a record as named keys each holding a different field.

**Why:** A list uses consecutive integer positions, while a record's string keys name its fields.

**Plausible wrong approach:** Storing a record as `['CSS', 55]` fails because code must remember that position 1 means minutes, which breaks when fields are added.

**How to verify:** Accessing `$row['minutes']` on the keyed record prints 55 and reads clearly in the code.

## Exercise 2: Add a second validated study row.

**Expected evidence:** Every row has the declared subject and integer-minutes fields.

**Approach:** Append a second array with the same `subject` and `minutes` keys, and check that minutes is an int with `is_int`.

**Why:** Records with the same keys and types can be processed by one function without special cases.

**Plausible wrong approach:** Spelling the key as `minute` in the new row fails because later code reads `minutes` and gets a missing key warning.

**How to verify:** A loop over both rows prints each subject and minutes with no warnings. `array_column($rows, 'minutes')` returns two integers, one per row.

## Exercise 3: Filter and summarize study records without changing the originals.

**Expected evidence:** The derived list contains only qualifying rows and retains consecutive indices.

**Approach:** Use `array_filter` with a typed arrow function, wrap it in `array_values`, then sum with `array_sum(array_column($visible, 'minutes'))`.

**Why:** array_filter returns a new array, and array_values renumbers it into a list.

**Plausible wrong approach:** Modifying `$rows` inside a `foreach` by reference fails because the original data changes and a later filter sees altered values.

**How to verify:** After the summary, dumping `$rows` shows the original records unchanged, and the derived list has keys 0 upward.

## Exercise 4: Diagnose JSON output changing from an array to an object shape.

**Expected answer:** Inspect numeric key gaps after filtering and reindex when the contract is a list.

**Approach:** Encode the filtered array, notice an object with numeric keys, and add `array_values` before encoding to restore a list.

**Why:** array_filter preserves keys, so gaps such as 0 and 2 make json_encode produce an object instead of a list.

**Plausible wrong approach:** Passing `JSON_FORCE_OBJECT` or changing the client fails because the real problem is the key gap in the PHP array.

**How to verify:** `json_encode` after reindexing prints a value that starts with `[` instead of `{`. A JavaScript client can then call `.map` on the parsed value without a TypeError.

## Exercise 5: Test an empty result and a missing required field.

**Expected evidence:** Empty lists are valid where declared; malformed records are rejected explicitly.

**Approach:** Run the filter with a threshold no row meets, and run validation on a row lacking `minutes`, recording both outcomes.

**Why:** An empty list is a valid result, while a malformed record must be rejected before it is used.

**Plausible wrong approach:** Using `$row['minutes'] ?? 0` for missing fields fails because a broken record silently becomes a valid zero minute session.

**How to verify:** The empty filter encodes as [] and the malformed row raises the declared validation error.

## Exercise 6: Explain the risk of a lingering foreach reference.

**Expected answer:** A reference variable can still alias the last element and cause later assignments to mutate it.

**Approach:** Call `unset($row)` after any `foreach ($rows as &$row)` loop so the reference no longer points at the last element.

**Why:** After a by-reference loop, `$item` still points at the last element, so a later assignment overwrites it; `unset($item)` breaks the reference.

**Plausible wrong approach:** Reusing `$row` in a second plain `foreach` fails because each assignment then overwrites the last element of the array.

**How to verify:** Without `unset`, the last record ends up duplicated; with `unset`, all records keep their original values.

## Reference comparison

Open `courses/web-development/solutions/web-035_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
