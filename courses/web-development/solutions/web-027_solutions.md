# web-027: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Validation becomes easier to test when a pure function receives data and returns errors without touching the document. The browser layer then displays those errors and moves focus only when it helps recovery. This separation lets the same input contract be tested with normal, missing and boundary values before considering visual presentation. It does not remove the need for backend validation.

An error summary gives a user an overview after an attempted action. Field-level messages explain how to repair specific values. Connect those messages to controls and preserve entered values. Avoid announcing a long stream of errors on every keystroke. The timing of feedback is a product decision that should reduce confusion rather than punish incomplete typing.

The reference uses a button to validate local values without submitting a form. Convert the input string carefully, reject empty strings before Number conversion and check Number.isFinite. Return an error list, then render it with textContent. Set aria-invalid only after a failed check. A valid result is a local observation, not a stored request.

## Exercise 1: Predict Number('') and explain the validation hazard.

It produces zero, so an explicit empty-input check prevents misleading acceptance or errors.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add the upper-bound case to a validation table.

120 is accepted and 121 is rejected under the declared inclusive bounds.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a local form with preserved input and linked validation feedback.

A failed attempt identifies the problem without clearing the user's value.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a message shown visually but not associated with its control.

Use a stable message id and aria-describedby on the input.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test empty, whitespace, negative, nonnumeric and valid values.

Each produces the declared result with no uncaught exception.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain which validation logic must be repeated on the server.

All acceptance and authorization rules must be enforced independently of client behavior.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
