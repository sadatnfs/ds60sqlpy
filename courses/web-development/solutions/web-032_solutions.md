# web-032: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-032.md`.

## Exercise 1: Predict strict equality for '0', 0 and false.

**Expected answer:** Each has a different type, so cross-type strict comparisons are false.

**Approach:** Note the type of each value, string, int and bool, and recall that `===` returns false whenever the two types differ.

**Why:** === compares type and value, so a string, an integer and a boolean are never strictly equal to each other.

**Plausible wrong approach:** Using `==` and reporting true fails because loose comparison converts types first and hides the distinction the question asks about.

**How to verify:** Running `var_export` on each strict pair prints false three times.

## Exercise 2: Add a typed diagnostic to a value before converting it.

**Expected evidence:** The output identifies the actual type rather than relying on its printed appearance.

**Approach:** Print `get_debug_type($value)` before converting, so the output names the actual type such as string or int.

**Why:** A typed diagnostic shows whether '0' is a string or an integer, which echo alone hides.

**Plausible wrong approach:** Printing the value with `echo` fails because '30' and 30 look identical in output while their types differ.

**How to verify:** The diagnostic line reads string for the raw input and int after the deliberate conversion.

## Exercise 3: Model an optional note without confusing missing, empty and null.

**Expected evidence:** The program documents and checks the chosen interpretation of each state.

**Approach:** Use `array_key_exists` to detect a missing key, then check for null, then check for an empty string, each with a stated meaning.

**Why:** array_key_exists distinguishes a missing key from a key holding null, while ?? treats both the same, so the chosen meaning must be explicit.

**Plausible wrong approach:** Using `empty($record['note'])` fails because it treats a missing key, null, '' and '0' as the same state.

**How to verify:** Four test records, missing, null, empty and a real note, each produce a different documented label.

## Exercise 4: Repair a loose comparison that accepts an unintended type.

**Expected evidence:** Use strict comparison after deliberate validation and conversion.

**Approach:** Validate the input with a pattern or a filter, convert it explicitly with `(int)`, and then compare with `===`.

**Why:** Loose comparison coerces types, so values such as '1' and true can compare equal unexpectedly; strict comparison after validation removes that surprise.

**Plausible wrong approach:** Adding a cast inside a loose comparison fails because the loose operator still accepts other spellings you did not intend.

**How to verify:** The repaired check rejects '1e1' when only '10' is allowed and accepts the exact expected value.

## Exercise 5: Test zero as a valid numeric boundary.

**Expected evidence:** Zero is retained when the contract permits it, rather than discarded as generic falsy data.

**Approach:** Run the program with 0 as a valid entry and confirm that a strict null check, not truthiness, decides whether it is kept.

**Why:** 0 is falsy, so a truthiness check such as `if ($minutes)` drops a valid zero; compare with null or use a range check instead.

**Plausible wrong approach:** Writing `if ($minutes)` fails because 0 is falsy, so a legitimate zero entry is skipped as if it were missing.

**How to verify:** The output lists the zero entry, and the total includes it as 0 rather than omitting the row.

## Exercise 6: Explain the limited scope of strict_types.

**Expected answer:** It affects relevant scalar call coercions; it does not replace runtime validation or static analysis.

**Approach:** State that `strict_types` changes how scalar arguments are coerced at function calls in this file, and nothing more.

**Why:** strict_types controls scalar coercion for calls made from that file; it does not validate ranges, formats or array contents at runtime.

**Plausible wrong approach:** Claiming strict mode validates form input fails because data from requests is still a string that needs explicit checks.

**How to verify:** Passing '30' to an `int` parameter under strict mode throws a TypeError, while comparisons elsewhere are unaffected.

## Reference comparison

Open `courses/web-development/solutions/web-032_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
