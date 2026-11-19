# web-009: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-009.md`.

## Exercise 1: Predict required, minimum and maximum outcomes for empty, 4, 30 and 121.

**Expected answer:** Empty, 4 and 121 fail; 30 satisfies the numeric bounds.

**Why:** An empty value fails required, 4 is below min and 121 is above max, while 30 satisfies every constraint.

## Exercise 2: Add a clear unit and range to a control's label.

**Expected evidence:** The rule is understandable before an error occurs.

**Why:** Stating the rule up front prevents errors instead of explaining them after a failed attempt.

## Exercise 3: Build a bounded study-time form with linked help.

**Expected evidence:** The user can identify the rule, enter a valid value and retain it after a failed attempt.

**Why:** aria-describedby makes the rule part of the field's announcement, and preserving the value lets the user correct it instead of retyping.

## Exercise 4: Explain why type=email does not prove mailbox ownership.

**Expected answer:** It checks a syntactic format, not identity or delivery.

**Why:** The browser checks only the address syntax; proving ownership requires sending a message and confirming the response.

## Exercise 5: Test validation with keyboard and an empty field.

**Expected evidence:** The error is discoverable and the entered values are preserved.

**Why:** Errors must be perceivable and reachable by keyboard, otherwise a keyboard user may not learn that the submission failed.

## Exercise 6: Separate client feedback from server-side acceptance.

**Expected evidence:** The backend repeats contract checks and authorization regardless of browser validation.

**Why:** Client constraints improve feedback but can be bypassed, so the server repeats validation and authorization before accepting data.

## Reference comparison

Open `courses/web-development/solutions/web-009_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
