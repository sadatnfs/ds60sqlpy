# web-019: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-019.md`.

## Exercise 1: Distinguish a condition selector from generated content.

**Expected answer:** A pseudo-class selects an existing state; a pseudo-element styles a represented part.

**Why:** A pseudo-class such as :focus selects existing elements in a state, while a pseudo-element such as ::before styles a generated part.

## Exercise 2: Add focus-within feedback around a labeled input.

**Expected evidence:** The group is highlighted while the control has focus.

**Why:** :focus-within matches an element when it or any descendant has focus, so the whole field group can change.

## Exercise 3: Build a preferences list whose selected state is visible and semantic.

**Expected evidence:** Native checkboxes carry the state and text styling reinforces it.

**Why:** The checkbox keeps the real state and keyboard behavior, and the sibling selector reflects that state visually.

## Exercise 4: Remove an essential instruction placed only in ::before and restore it as HTML.

**Expected evidence:** The instruction becomes real document content available independently of generated decoration.

**Why:** Generated content is not reliably exposed to assistive technology or copy and paste, so essential text belongs in the document.

## Exercise 5: Operate the controls without hover.

**Expected evidence:** All actions and state information remain usable by keyboard and touch.

**Why:** Hover is unavailable on touch and keyboard, so anything shown only on hover is lost to those users.

## Exercise 6: Explain why CSS state cannot authorize a server action.

**Expected answer:** Presentation can be changed by the client; the server must enforce permission using trusted context.

**Why:** Users can change styles and requests freely, so permission decisions must use trusted server-side identity and data.

## Reference comparison

Open `courses/web-development/solutions/web-019_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
