# web-026: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-026.md`.

## Exercise 1: Choose a disclosure or dialog for an optional explanation.

**Expected answer:** A disclosure usually fits because it preserves the surrounding reading context.

**Why:** A disclosure keeps the explanation in place and does not interrupt the task, while a modal dialog blocks the rest of the page.

## Exercise 2: Give a dialog a visible heading and accessible name.

**Expected evidence:** aria-labelledby connects it to the heading's unique id.

**Why:** aria-labelledby makes the visible heading the dialog's accessible name, so it is announced when the dialog opens.

## Exercise 3: Build a disclosure and a deliberately opened local dialog.

**Expected evidence:** Both are labeled, keyboard operable and can be closed without losing the task.

**Why:** Native details and dialog elements provide keyboard support, Escape handling and the top layer without custom focus code.

## Exercise 4: Diagnose focus returning to an unrelated control after closure.

**Expected answer:** Track the opener and restore focus when appropriate.

**Why:** Returning focus to the opener keeps keyboard users at the same place in the task.

## Exercise 5: Test Escape, close-button activation and repeated opening.

**Expected evidence:** The interaction remains consistent across repeated cycles and does not trap focus.

**Why:** Repeated cycles reveal leaks such as duplicate listeners or focus moving to the page start.

## Exercise 6: Explain why a modal is inappropriate for every small message.

**Expected answer:** It interrupts context and imposes focus management costs that a simple inline message avoids.

**Why:** A modal blocks the page and requires focus management, which a short inline message does not need.

## Reference comparison

Open `courses/web-development/solutions/web-026_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
