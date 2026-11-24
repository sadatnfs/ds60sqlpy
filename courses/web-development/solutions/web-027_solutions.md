# web-027: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-027.md`.

## Exercise 1: Predict Number('') and explain the validation hazard.

**Expected answer:** It produces zero, so an explicit empty-input check prevents misleading acceptance or errors.

**Approach:** Evaluate `Number('')`, see that it returns 0, and note that 0 is a valid number that fails the range check for the wrong reason.

**Why:** Number('') returns 0, a finite number, so without an explicit empty check a blank field reaches the range check and gets the wrong message.

**Plausible wrong approach:** Checking `Number.isNaN` alone fails because an empty field converts to 0, not NaN, and slips past that test.

**How to verify:** Logging `Number('')` prints 0, and the strict validator returns Enter minutes. for both '' and '   '.

## Exercise 2: Add the upper-bound case to a validation table.

**Expected evidence:** 120 is accepted and 121 is rejected under the declared inclusive bounds.

**Approach:** Add rows for 120 and 121 to the table and run each through `validate`, keeping the comparison as `minutes <= 120`.

**Why:** Inclusive bounds accept the boundary value, so 120 passes and 121 fails; testing both sides catches off-by-one errors.

**Plausible wrong approach:** Writing `minutes < 120` fails because the declared bounds are inclusive, so a valid 120 would be rejected.

**How to verify:** The table shows '' returned for 120 and Use 5 to 120 minutes. returned for 121.

## Exercise 3: Build a local form with preserved input and linked validation feedback.

**Expected evidence:** A failed attempt identifies the problem without clearing the user's value.

**Approach:** Validate on a button click, write any message with `textContent` into an element whose `id` the input lists in `aria-describedby`, and never clear the input.

**Why:** Keeping the value lets the user correct the mistake, and a linked message explains what to change.

**Plausible wrong approach:** Resetting the form after an error fails because the reader must retype everything and cannot see what was wrong.

**How to verify:** Enter 200, validate, and see the message beside the field while 200 is still in the input.

## Exercise 4: Diagnose a message shown visually but not associated with its control.

**Expected answer:** Use a stable message id and aria-describedby on the input.

**Approach:** Give the error element a stable `id` and add that `id` to the input's `aria-describedby` attribute.

**Why:** aria-describedby makes the message part of the input's accessible description, so it is announced with the field.

**Plausible wrong approach:** Placing the message near the field with only CSS proximity fails because assistive technology does not link nearby text to the input.

**How to verify:** The input's description in the accessibility panel contains the current error text.

## Exercise 5: Test empty, whitespace, negative, nonnumeric, hexadecimal (0x1e), exponent (1e2), fractional (7.5) and valid values.

**Expected evidence:** Each produces the declared result with no uncaught exception.

**Approach:** Run each listed input through `validate` in a table and record the exact returned string next to the expected one.

**Why:** Number accepts 0x1e, 1e2 and 7.5, so only the digits-only check rejects them; a loop shows that every case returns a message instead of throwing.

**Plausible wrong approach:** Testing only 30 and abc fails because hexadecimal, exponent and fractional strings are the ones a looser rule wrongly accepts.

**How to verify:** 0x1e, 1e2 and 7.5 each return Use whole minutes from 5 to 120., and ' 30 ' returns an empty string.

## Exercise 6: Explain which validation logic must be repeated on the server.

**Expected answer:** All acceptance and authorization rules must be enforced independently of client behavior.

**Approach:** Repeat every acceptance rule on the server, because the server receives raw requests that may never have run this script.

**Why:** Any client can send data without running this script, so the server must repeat every acceptance and authorization rule.

**Plausible wrong approach:** Trusting a hidden flag that says the client validated fails because a request tool can send the flag with any value.

**How to verify:** A direct request with minutes=0x1e is rejected by the server rule taught in web-047.

## Reference comparison

Open `courses/web-development/solutions/web-027_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
