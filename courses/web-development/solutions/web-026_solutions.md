# web-026: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A disclosure reveals content in the current document, while a dialog creates a focused interaction context. These are different patterns and should not be chosen only for visual style. Native details and summary elements provide a useful disclosure without JavaScript. A modal dialog changes which content can be interacted with and needs a clear way to close, an accessible name and sensible focus restoration.

Focus is part of the interaction's state. When a dialog opens, the user should land in a meaningful place. When it closes, focus usually returns to the control that opened it if that control still exists. Keyboard users must not become trapped in an accidental custom implementation. Native dialog behavior supplies important mechanics, but authors still own labeling, content order and testing.

Use details with summary for optional explanation. Use a dialog element and showModal when a true modal task is justified. A form with method=dialog can close the dialog; this local behavior is distinct from a network form submission. The offline preview may restrict submission APIs, so this reference closes explicitly through the dialog API and keeps all state local.

## Exercise 1: Choose a disclosure or dialog for an optional explanation.

A disclosure usually fits because it preserves the surrounding reading context.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Give a dialog a visible heading and accessible name.

aria-labelledby connects it to the heading's unique id.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a disclosure and a deliberately opened local dialog.

Both are labeled, keyboard operable and can be closed without losing the task.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose focus returning to an unrelated control after closure.

Track the opener and restore focus when appropriate.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test Escape, close-button activation and repeated opening.

The interaction remains consistent across repeated cycles and does not trap focus.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why a modal is inappropriate for every small message.

It interrupts context and imposes focus management costs that a simple inline message avoids.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
