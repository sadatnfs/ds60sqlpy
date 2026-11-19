# web-025: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-025.md`.

## Exercise 1: Predict when the registered callback executes.

**Expected answer:** It runs on a matching event, not merely because the listener was registered.

**Why:** addEventListener stores the callback; the browser calls it later, once per matching event.

## Exercise 2: Change the display label without changing numeric state.

**Expected evidence:** The counter logic remains independent of presentation wording.

**Why:** Keeping state separate from presentation lets the wording change without breaking the arithmetic.

## Exercise 3: Build a native-button counter with a reset action and output.

**Expected evidence:** Increment and reset work by keyboard and pointer, with a visible announced result.

**Why:** Native buttons are keyboard operable, and output can be announced as a status when its text changes.

## Exercise 4: Diagnose a null selection caused by a missing id.

**Expected answer:** Inspect the document relationship before attaching the listener.

**Why:** querySelector returns null when no element matches, and calling a method on null throws a TypeError.

## Exercise 5: Insert text containing angle brackets without creating markup.

**Expected evidence:** textContent preserves the literal data and creates no extra element.

**Why:** textContent stores characters as text, so angle brackets never reach the HTML parser and cannot create elements.

## Exercise 6: Explain why reading state back from formatted text is fragile.

**Expected answer:** Formatting, localization and extra words can break parsing while the underlying number is unchanged.

**Why:** Parsing formatted text couples logic to presentation, so a translation or extra word breaks the state.

## Reference comparison

Open `courses/web-development/solutions/web-025_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
