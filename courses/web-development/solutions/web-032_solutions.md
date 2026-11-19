# web-032: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-032.md`.

## Exercise 1: Predict strict equality for '0', 0 and false.

**Expected answer:** Each has a different type, so cross-type strict comparisons are false.

**Why:** === compares type and value, so a string, an integer and a boolean are never strictly equal to each other.

## Exercise 2: Add a typed diagnostic to a value before converting it.

**Expected evidence:** The output identifies the actual type rather than relying on its printed appearance.

**Why:** A typed diagnostic shows whether '0' is a string or an integer, which echo alone hides.

## Exercise 3: Model an optional note without confusing missing, empty and null.

**Expected evidence:** The program documents and checks the chosen interpretation of each state.

**Why:** array_key_exists distinguishes a missing key from a key holding null, while ?? treats both the same, so the chosen meaning must be explicit.

## Exercise 4: Repair a loose comparison that accepts an unintended type.

**Expected evidence:** Use strict comparison after deliberate validation and conversion.

**Why:** Loose comparison coerces types, so values such as '1' and true can compare equal unexpectedly; strict comparison after validation removes that surprise.

## Exercise 5: Test zero as a valid numeric boundary.

**Expected evidence:** Zero is retained when the contract permits it, rather than discarded as generic falsy data.

**Why:** 0 is falsy, so a truthiness check such as `if ($minutes)` drops a valid zero; compare with null or use a range check instead.

## Exercise 6: Explain the limited scope of strict_types.

**Expected answer:** It affects relevant scalar call coercions; it does not replace runtime validation or static analysis.

**Why:** strict_types controls scalar coercion for calls made from that file; it does not validate ranges, formats or array contents at runtime.

## Reference comparison

Open `courses/web-development/solutions/web-032_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
