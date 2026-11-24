# web-008: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-008.md`.

## Exercise 1: Predict the different roles of id and name.

**Expected answer:** Id supports document relationships; name identifies the submitted field.

**Approach:** Separate the two jobs: `id` links a label and other in-page references, while `name` becomes the key in submitted data.

**Why:** id connects document relationships such as label for, while name is the key used for the value in the submitted form data.

**Plausible wrong approach:** Assuming the `id` doubles as the submitted key fails because a control with only an `id` is left out of `FormData`.

**How to verify:** Logging `[...new FormData(form)]` shows the `name` values as keys and never the `id` values.

## Exercise 2: Add a textarea with a persistent label.

**Expected evidence:** The label remains available while the user types.

**Approach:** Add a `label for="notes"` and a `textarea id="notes" name="notes"`, keeping the label visible above the field.

**Why:** Placeholder text disappears while typing and often has low contrast; a label stays visible and is announced as the field's name.

**Plausible wrong approach:** Using only `placeholder` as the label fails because the hint disappears as soon as the user starts typing.

**How to verify:** Clicking the label text focuses the textarea, and the label is still visible after you type a sentence.

## Exercise 3: Build a study-preferences form with three native control types.

**Expected evidence:** Every control has a useful label, stable name and suitable type.

**Approach:** Choose three native types such as `text`, `select` and `checkbox`, and give each one a label, an `id` and a stable `name`.

**Why:** Native controls provide keyboard support, accessible roles and correct submitted values without extra scripting.

**Plausible wrong approach:** Building a custom dropdown from `div` elements fails because it loses native keyboard handling and form participation.

**How to verify:** `FormData` lists every named control, and each control's accessible name in the accessibility panel matches its label.

## Exercise 4: Diagnose a field missing from submitted values.

**Expected answer:** Check name, disabled state and the control's successful-value rules.

**Approach:** Check the missing field in order: does it have a `name`, is it `disabled`, and for checkboxes, is it actually checked?

**Why:** Only successful controls are submitted: a control without a name, a disabled control or an unchecked checkbox contributes nothing.

**Plausible wrong approach:** Blaming the server first fails because the browser never put the field into the request in this case.

**How to verify:** After adding `name` or removing `disabled`, the field appears in the `FormData` console listing.

## Exercise 5: Navigate the form using only Tab and Space.

**Expected evidence:** Each enabled control is reachable and can be operated without a pointer.

**Approach:** Start before the first field and press Tab through each control, using Space for checkboxes and arrow keys inside `select`.

**Why:** Native controls are focusable and operable by keyboard by default, while custom widgets often lose this unless they are built carefully.

**Plausible wrong approach:** Adding `tabindex="5"` style positive values to force an order fails because it overrides document order and confuses every later control.

**How to verify:** Focus moves in source order to every enabled control, and each one can be changed without a mouse.

## Exercise 6: Explain why form appearance cannot establish server validation.

**Expected answer:** Client controls guide entry; a server must independently validate incoming data.

**Approach:** Contrast what the browser controls with what an attacker controls: any request can be crafted without your HTML form.

**Why:** Anything the browser enforces can be changed or skipped by the client, so the server must validate every field itself.

**Plausible wrong approach:** Treating `maxlength` or a `select` list as a server guarantee fails because a crafted request can send any value or length.

**How to verify:** Editing a field's `maxlength` in the Elements panel lets you enter a longer value, showing the client rule is changeable.

## Reference comparison

Open `courses/web-development/solutions/web-008_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
