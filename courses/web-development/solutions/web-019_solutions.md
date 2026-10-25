# web-019: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A pseudo-class selects an element based on a condition such as focus, checked state or its position among siblings. A pseudo-element represents a stylable part associated with an element, such as before or after. Generated decorative content can enrich presentation, but essential instructions should exist as real document content because generated content has inconsistent accessibility implications.

State should remain grounded in a real control or application contract. Styling a checkbox's checked state makes use of built-in behavior. A decorative class named active does not prove that a control is selected, and CSS cannot perform server authorization. Use native state first and add custom state only with a clear interaction model.

`:focus-within` matches a container while one of its descendants has focus. `input:checked + span` selects a neighboring label fragment after a checked input. Attribute selectors can target a declared state, but the application is responsible for keeping that state accurate. Hover must be an enhancement because touch and keyboard interactions may not provide the same hover behavior.

## Exercise 1: Distinguish a condition selector from generated content.

A pseudo-class selects an existing state; a pseudo-element styles a represented part.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add focus-within feedback around a labeled input.

The group is highlighted while the control has focus.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a preferences list whose selected state is visible and semantic.

Native checkboxes carry the state and text styling reinforces it.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Remove an essential instruction placed only in ::before and restore it as HTML.

The instruction becomes real document content available independently of generated decoration.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Operate the controls without hover.

All actions and state information remain usable by keyboard and touch.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why CSS state cannot authorize a server action.

Presentation can be changed by the client; the server must enforce permission using trusted context.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
