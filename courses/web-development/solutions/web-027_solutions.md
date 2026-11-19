# web-027: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-027.md`.

## Exercise 1: Predict Number('') and explain the validation hazard.

**Expected answer:** It produces zero, so an explicit empty-input check prevents misleading acceptance or errors.

**Why:** Number('') returns 0, a finite number, so without an explicit empty check a blank field reaches the range check and gets the wrong message.

## Exercise 2: Add the upper-bound case to a validation table.

**Expected evidence:** 120 is accepted and 121 is rejected under the declared inclusive bounds.

**Why:** Inclusive bounds accept the boundary value, so 120 passes and 121 fails; testing both sides catches off-by-one errors.

## Exercise 3: Build a local form with preserved input and linked validation feedback.

**Expected evidence:** A failed attempt identifies the problem without clearing the user's value.

**Why:** Keeping the value lets the user correct the mistake, and a linked message explains what to change.

## Exercise 4: Diagnose a message shown visually but not associated with its control.

**Expected answer:** Use a stable message id and aria-describedby on the input.

**Why:** aria-describedby makes the message part of the input's accessible description, so it is announced with the field.

## Exercise 5: Test empty, whitespace, negative, nonnumeric, hexadecimal (0x1e), exponent (1e2), fractional (7.5) and valid values.

**Expected evidence:** Each produces the declared result with no uncaught exception.

**Why:** Number accepts 0x1e, 1e2 and 7.5, so only the digits-only check rejects them; a loop shows that every case returns a message instead of throwing.

## Exercise 6: Explain which validation logic must be repeated on the server.

**Expected answer:** All acceptance and authorization rules must be enforced independently of client behavior.

**Why:** Any client can send data without running this script, so the server must repeat every acceptance and authorization rule.

## Reference comparison

Open `courses/web-development/solutions/web-027_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
