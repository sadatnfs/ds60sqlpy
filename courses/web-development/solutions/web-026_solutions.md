# web-026: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-026.md`.

## Exercise 1: Choose a disclosure or dialog for an optional explanation.

**Expected answer:** A disclosure usually fits because it preserves the surrounding reading context.

**Approach:** Ask whether the reader must stop and act before continuing; optional explanation should stay inline, beside the text it explains.

**Why:** A disclosure keeps the explanation in place and does not interrupt the task, while a modal dialog blocks the rest of the page.

**Plausible wrong approach:** Choosing a modal dialog fails because it blocks the page and hides the paragraph the reader was trying to understand.

**How to verify:** With `details`, the reader can expand the explanation and still scroll and read the surrounding text.

## Exercise 2: Give a dialog a visible heading and accessible name.

**Expected evidence:** aria-labelledby connects it to the heading's unique id.

**Approach:** Put an `h2` with a unique `id` inside the dialog and point the dialog's `aria-labelledby` at that `id`.

**Why:** aria-labelledby makes the visible heading the dialog's accessible name, so it is announced when the dialog opens.

**Plausible wrong approach:** Using `aria-label` with text that differs from the visible heading fails because speech and screen output then disagree.

**How to verify:** The accessibility tree lists the dialog with the visible heading text as its name.

## Exercise 3: Build a disclosure and a deliberately opened local dialog.

**Expected evidence:** Both are labeled, keyboard operable and can be closed without losing the task.

**Approach:** Combine a `details` element for the explanation with a `dialog` opened by `showModal()` from a button and closed by `close()` from another.

**Why:** Native details and dialog elements provide keyboard support, Escape handling and the top layer without custom focus code.

**Plausible wrong approach:** Opening the dialog automatically on page load fails because it interrupts reading before the learner asked for anything.

**How to verify:** The dialog appears only after activating the open button, and both closing methods return the page to normal.

## Exercise 4: Diagnose focus returning to an unrelated control after closure.

**Expected answer:** Track the opener and restore focus when appropriate.

**Approach:** Store the opener element when opening, and on the dialog's `close` event call `opener.focus()` if it is still in the document.

**Why:** Returning focus to the opener keeps keyboard users at the same place in the task.

**Plausible wrong approach:** Focusing the first link on the page after closing fails because the reader loses their place and must tab back.

**How to verify:** After closing, `document.activeElement` is the button that opened the dialog.

## Exercise 5: Test Escape, close-button activation and repeated opening.

**Expected evidence:** The interaction remains consistent across repeated cycles and does not trap focus.

**Approach:** Open and close the dialog three times, alternating Escape and the close button, and press Tab inside it each cycle.

**Why:** Repeated cycles reveal leaks such as duplicate listeners or focus moving to the page start.

**Plausible wrong approach:** Testing only one open and close fails because duplicate listeners or stale state often appear only on the second cycle.

**How to verify:** Each cycle opens the dialog once, keeps Tab inside it, and returns focus to the opener after closing.

## Exercise 6: Explain why a modal is inappropriate for every small message.

**Expected answer:** It interrupts context and imposes focus management costs that a simple inline message avoids.

**Approach:** Weigh the cost of interruption, inert background and focus handling against the message, and use inline text for small confirmations.

**Why:** A modal blocks the page and requires focus management, which a short inline message does not need.

**Plausible wrong approach:** Using a modal for a Saved locally note fails because the reader must dismiss it before continuing, for no decision.

**How to verify:** An inline status message beside the button is read without any extra keystroke and leaves focus where it was.

## Reference comparison

Open `courses/web-development/solutions/web-026_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
