# web-009: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Validation checks whether input satisfies a contract. Browser constraint validation gives immediate feedback through attributes such as required, type, min and maxlength. It improves the interaction but is not a security boundary because a client can bypass it or send a request without using the form at all. A server must repeat the relevant validation and authorization decisions.

An error message should identify the field, explain the problem and offer a useful correction without losing the user's work. Color alone is insufficient. Connect instructions and errors with aria-describedby, and use aria-invalid when an actual invalid state has been identified. Do not mark every untouched field invalid when the page first opens.

`checkValidity()` reports whether a control meets its constraints. `reportValidity()` also requests the browser's feedback interface. An empty required field is invalid, while a non-required empty email field may be valid. Email type checks syntax, not whether the mailbox exists or belongs to the user. This lesson uses native constraints and explicit explanatory text; it does not send data.

## Exercise 1: Predict required, minimum and maximum outcomes for empty, 4, 30 and 121.

Empty, 4 and 121 fail; 30 satisfies the numeric bounds.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a clear unit and range to a control's label.

The rule is understandable before an error occurs.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a bounded study-time form with linked help.

The user can identify the rule, enter a valid value and retain it after a failed attempt.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why type=email does not prove mailbox ownership.

It checks a syntactic format, not identity or delivery.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test validation with keyboard and an empty field.

The error is discoverable and the entered values are preserved.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Separate client feedback from server-side acceptance.

The backend repeats contract checks and authorization regardless of browser validation.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
