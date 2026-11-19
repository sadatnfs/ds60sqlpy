# web-008: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-008.md`.

## Exercise 1: Predict the different roles of id and name.

**Expected answer:** Id supports document relationships; name identifies the submitted field.

**Why:** id connects document relationships such as label for, while name is the key used for the value in the submitted form data.

## Exercise 2: Add a textarea with a persistent label.

**Expected evidence:** The label remains available while the user types.

**Why:** Placeholder text disappears while typing and often has low contrast; a label stays visible and is announced as the field's name.

## Exercise 3: Build a study-preferences form with three native control types.

**Expected evidence:** Every control has a useful label, stable name and suitable type.

**Why:** Native controls provide keyboard support, accessible roles and correct submitted values without extra scripting.

## Exercise 4: Diagnose a field missing from submitted values.

**Expected answer:** Check name, disabled state and the control's successful-value rules.

**Why:** Only successful controls are submitted: a control without a name, a disabled control or an unchecked checkbox contributes nothing.

## Exercise 5: Navigate the form using only Tab and Space.

**Expected evidence:** Each enabled control is reachable and can be operated without a pointer.

**Why:** Native controls are focusable and operable by keyboard by default, while custom widgets often lose this unless they are built carefully.

## Exercise 6: Explain why form appearance cannot establish server validation.

**Expected answer:** Client controls guide entry; a server must independently validate incoming data.

**Why:** Anything the browser enforces can be changed or skipped by the client, so the server must validate every field itself.

## Reference comparison

Open `courses/web-development/solutions/web-008_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
