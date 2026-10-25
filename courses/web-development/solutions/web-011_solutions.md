# web-011: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Every rendered box has content, optional padding, a border and an outside margin. With the default content-box sizing, a declared width describes the content, so padding and borders add to the outer width. With border-box sizing, the declared width includes the content, padding and borders. Margins remain outside either calculation. This distinction explains many layouts that unexpectedly exceed a parent.

Overflow occurs when content needs more room than the available box. Hiding overflow can conceal essential information; scrolling or wrapping may preserve it. Long unbroken strings and images are frequent sources of overflow. A fixed height can clip translated text, enlarged fonts or error messages, so prefer content-driven height unless the interaction truly requires a bounded region.

For a 200px content-box with 20px left and right padding and 2px borders, outer width is 244px. For a 200px border-box, the content width becomes 156px. Set a consistent box-sizing rule on all elements and pseudo-elements. Use max-inline-size to constrain readable width without assuming the writing direction.

## Exercise 1: Calculate outer widths for the two examples.

They are 244px and 200px, before margins.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add border-box sizing to a document and inspect one card.

The declared width matches the border-box width.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a readable card that contains a long identifier.

The identifier wraps or scrolls locally without overflowing the page.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Repair a fixed height that clips a validation message.

Use content-driven height or an explicitly accessible bounded scroll region.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Increase text size and inspect overflow.

Essential text remains visible and controls remain reachable.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain which dimensions margin does and does not affect.

Margins add external separation but are not included in either box-sizing width.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
