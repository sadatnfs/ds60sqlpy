# web-019: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-019.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Distinguish a condition selector from generated content.

**Expected answer:** A pseudo-class selects an existing state; a pseudo-element styles a represented part.

**Approach:** Ask whether the selector matches an element in a state, such as `:checked`, or creates a stylable part, such as `::before`.

**Why:** A pseudo-class such as :focus selects existing elements in a state, while a pseudo-element such as ::before styles a generated part.

**Plausible wrong approach:** Calling `::before` a state fails because it never matches a condition; it creates a box that exists only for presentation.

**How to verify:** The Elements panel shows `::before` as a pseudo node inside the element, while `:checked` appears only as a matched selector.

## Exercise 2: Add focus-within feedback around a labeled input.

**Expected evidence:** The group is highlighted while the control has focus.

**Approach:** Wrap the label and input in a `.field` container and add a `:focus-within` border color to that container.

**Why:** :focus-within matches an element when it or any descendant has focus, so the whole field group can change.

**Plausible wrong approach:** Using `.field:focus` fails because the container itself never receives focus, so the rule never matches.

**How to verify:** Tab into the input and the field border changes; tab out and the border returns to its default.

## Exercise 3: Build a preferences list whose selected state is visible and semantic.

**Expected evidence:** Native checkboxes carry the state and text styling reinforces it.

**Approach:** Use native checkboxes inside labels and style `input:checked + span` so text weight reinforces the checked state.

**Why:** The checkbox keeps the real state and keyboard behavior, and the sibling selector reflects that state visually.

**Plausible wrong approach:** Building toggles from `span` elements with a `selected` class fails because no state reaches assistive technology or keyboard users.

**How to verify:** Pressing Space on a focused checkbox toggles it, its accessible state changes, and the adjacent text becomes bold.

## Exercise 4: Remove an essential instruction placed only in ::before and restore it as HTML.

**Expected evidence:** The instruction becomes real document content available independently of generated decoration.

**Approach:** Move the instruction text into a real element in HTML and connect it to the field with `aria-describedby`.

**Why:** Generated content is not reliably exposed to assistive technology or copy and paste, so essential text belongs in the document.

**Plausible wrong approach:** Adding `aria-label` to the pseudo element fails because pseudo elements are not DOM nodes and cannot carry attributes.

**How to verify:** Selecting all text on the page now includes the instruction, and the input's description lists it.

## Exercise 5: Operate the controls without hover.

**Expected evidence:** All actions and state information remain usable by keyboard and touch.

**Approach:** Disconnect the mouse mentally: reach every control with Tab, toggle with Space or Enter, and read each state without hovering.

**Why:** Hover is unavailable on touch and keyboard, so anything shown only on hover is lost to those users.

**Plausible wrong approach:** Revealing state only on `:hover` fails because keyboard and touch users never trigger hover in a dependable way.

**How to verify:** Every state label is visible without hovering, and each action is completed using only the keyboard.

## Exercise 6: Explain why CSS state cannot authorize a server action.

**Expected answer:** Presentation can be changed by the client; the server must enforce permission using trusted context.

**Approach:** Note that any CSS state can be changed in developer tools, so permission must be checked by the server using its own session.

**Why:** Users can change styles and requests freely, so permission decisions must use trusted server-side identity and data.

**Plausible wrong approach:** Hiding an admin button with `display: none` fails because the endpoint still accepts a request sent directly.

**How to verify:** Unhiding the button in developer tools shows it again, proving the style held no security decision.

## Reference comparison

The reference counts checked inputs and requires exactly one, so it catches a starter whose initial selection changed. It does not test the visible checked style, focus-within feedback or keyboard operation, so tab through the reminders, toggle each with Space and compare what changes on screen.

Open `courses/web-development/solutions/web-019_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
