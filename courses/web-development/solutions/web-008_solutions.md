# web-008: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A form collects values for an action. A label names a control; a placeholder offers a short example and disappears during entry, so it cannot replace a label. A control's id connects it to a label. Its name identifies the value when a browser constructs form data. These are different responsibilities, and a visible input without a name may not be submitted.

Choose the native control that matches the task. A select presents a bounded choice, a textarea accepts multiline text, and checkboxes represent independent choices. A radio group represents one choice among alternatives and shares a name. A fieldset and legend describe a related group. Native controls provide interaction and accessibility behavior that a custom drawing would need to recreate.

Connect `label for="topic"` with `input id="topic" name="topic"`. A button inside a form defaults to submission, so specify its type. Disabled controls are not included in submitted form data; readonly text controls can still contribute values. This offline preview prevents real submission. Inspect control values and labels without contacting a backend.

## Exercise 1: Predict the different roles of id and name.

Id supports document relationships; name identifies the submitted field.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a textarea with a persistent label.

The label remains available while the user types.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a study-preferences form with three native control types.

Every control has a useful label, stable name and suitable type.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a field missing from submitted values.

Check name, disabled state and the control's successful-value rules.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Navigate the form using only Tab and Space.

Each enabled control is reachable and can be operated without a pointer.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why form appearance cannot establish server validation.

Client controls guide entry; a server must independently validate incoming data.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
