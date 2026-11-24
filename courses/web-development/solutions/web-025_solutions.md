# web-025: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-025.md`.

## Exercise 1: Predict when the registered callback executes.

**Expected answer:** It runs on a matching event, not merely because the listener was registered.

**Approach:** Separate registration from execution: `addEventListener` stores the function now, and the browser calls it later each time a click happens.

**Why:** addEventListener stores the callback; the browser calls it later, once per matching event.

**Plausible wrong approach:** Saying the callback runs when the page loads fails because registering a listener only stores the function and runs none of its code.

**How to verify:** Put `console.log` inside the callback; the message appears only after each click, never during page load.

## Exercise 2: Change the display label without changing numeric state.

**Expected evidence:** The counter logic remains independent of presentation wording.

**Approach:** Keep `count` as the number and build the display text from it in one place, such as `output.textContent = 'Total: ' + count`.

**Why:** Keeping state separate from presentation lets the wording change without breaking the arithmetic.

**Plausible wrong approach:** Storing the label in the same variable as the count fails because `count += 1` then appends text instead of adding one.

**How to verify:** Rename the label to Clicks so far and click twice; the number still reads 2.

## Exercise 3: Build a native-button counter with a reset action and output.

**Expected evidence:** Increment and reset work by keyboard and pointer, with a visible announced result.

**Approach:** Use two native buttons with `type="button"`, one `output` element, a numeric `count`, an increment listener and a reset listener.

**Why:** Native buttons are keyboard operable, and output can be announced as a status when its text changes.

**Plausible wrong approach:** Making the controls from `div` elements with click handlers fails because they are not focusable and ignore Enter and Space.

**How to verify:** Tab to Add, press Enter twice and Space once, then reset; the output shows 3 and then 0.

## Exercise 4: Diagnose a null selection caused by a missing id.

**Expected answer:** Inspect the document relationship before attaching the listener.

**Approach:** Read the selector, search the HTML for that exact `id`, and check whether the script runs before or after the element is parsed.

**Why:** querySelector returns null when no element matches, and calling a method on null throws a TypeError.

**Plausible wrong approach:** Wrapping the call in `try` and ignoring the error fails because the button then silently has no listener at all.

**How to verify:** Logging `document.querySelector('#add')` prints the button element instead of null after the fix.

## Exercise 5: Insert text containing angle brackets without creating markup.

**Expected evidence:** textContent preserves the literal data and creates no extra element.

**Approach:** Assign the string `'<new learner>'` with `textContent` and inspect the DOM to count the element children of the label.

**Why:** textContent stores characters as text, so angle brackets never reach the HTML parser and cannot create elements.

**Plausible wrong approach:** Using `innerHTML` for the same string fails because the browser parses it as markup and may create an unknown element.

**How to verify:** The label shows the angle brackets literally, and the Elements panel shows only a text node inside it.

## Exercise 6: Explain why reading state back from formatted text is fragile.

**Expected answer:** Formatting, localization and extra words can break parsing while the underlying number is unchanged.

**Approach:** Keep a numeric variable as the source of truth and treat the visible text as output only, regenerated after each change.

**Why:** Parsing formatted text couples logic to presentation, so a translation or extra word breaks the state.

**Plausible wrong approach:** Reading `parseInt(output.textContent)` fails as soon as the text becomes Total: 3 or uses a localized format such as 1.000.

**How to verify:** Change the display format to Total: 3 and confirm the next click still shows Total: 4.

## Reference comparison

Open `courses/web-development/solutions/web-025_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
