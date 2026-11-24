# web-009: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-009.md`.

## Exercise 1: Predict required, minimum and maximum outcomes for empty, 4, 30 and 121.

**Expected answer:** Empty, 4 and 121 fail; 30 satisfies the numeric bounds.

**Approach:** Check each value against `required`, `min="5"` and `max="120"` separately, then combine the results.

**Why:** An empty value fails required, 4 is below min and 121 is above max, while 30 satisfies every constraint.

**Plausible wrong approach:** Treating 121 as acceptable because it is a valid number fails because `max="120"` sets `rangeOverflow` for it.

**How to verify:** Set each value in the console and read `checkValidity()`: false for empty, 4 and 121, true for 30.

## Exercise 2: Add a clear unit and range to a control's label.

**Expected evidence:** The rule is understandable before an error occurs.

**Approach:** Put the unit and the allowed range in the visible label text, such as Minutes, 5 to 120.

**Why:** Stating the rule up front prevents errors instead of explaining them after a failed attempt.

**Plausible wrong approach:** Stating the range only in the error message fails because users learn the rule only after making a mistake.

**How to verify:** The label text read in the accessibility panel includes the unit and both limits before any input.

## Exercise 3: Build a bounded study-time form with linked help.

**Expected evidence:** The user can identify the rule, enter a valid value and retain it after a failed attempt.

**Approach:** Combine the bounded number input with a help paragraph referenced by `aria-describedby`, and keep the form from clearing on failure.

**Why:** aria-describedby makes the rule part of the field's announcement, and preserving the value lets the user correct it instead of retyping.

**Plausible wrong approach:** Calling `form.reset()` inside the invalid handler fails because it erases the user's valid entries along with the bad one.

**How to verify:** Enter 4, attempt to submit, and confirm the field still shows 4 with the help text announced as its description.

## Exercise 4: Explain why type=email does not prove mailbox ownership.

**Expected answer:** It checks a syntactic format, not identity or delivery.

**Approach:** Separate format from ownership: `type="email"` matches a syntax pattern, while ownership needs a message the person must act on.

**Why:** The browser checks only the address syntax; proving ownership requires sending a message and confirming the response.

**Plausible wrong approach:** Treating a valid-looking address as verified fails because anyone can type someone else's well-formed address.

**How to verify:** `a@b.example` passes `checkValidity()` even though that mailbox does not exist.

## Exercise 5: Test validation with keyboard and an empty field.

**Expected evidence:** The error is discoverable and the entered values are preserved.

**Approach:** Leave the field empty, use Tab to reach the submit button, press Enter, and listen or look for the browser's message.

**Why:** Errors must be perceivable and reachable by keyboard, otherwise a keyboard user may not learn that the submission failed.

**Plausible wrong approach:** Testing only with a mouse click fails to show whether focus returns to the invalid field for keyboard users.

**How to verify:** After the attempt, focus sits on the empty required field and the other fields keep their typed values.

## Exercise 6: Separate client feedback from server-side acceptance.

**Expected evidence:** The backend repeats contract checks and authorization regardless of browser validation.

**Approach:** List each rule twice: once as client feedback in the form, and once as a server check that runs on every request.

**Why:** Client constraints improve feedback but can be bypassed, so the server repeats validation and authorization before accepting data.

**Plausible wrong approach:** Removing the server check because the form already validates fails because a request sent without the form skips every browser rule.

**How to verify:** Your list shows the range rule present on both the client and the server, with authorization only on the server.

## Reference comparison

Open `courses/web-development/solutions/web-009_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
