# web-014: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Normal flow is the browser's default arrangement of content. Block boxes generally stack in the block direction and inline content flows within lines. Understanding this default prevents unnecessary positioning. Display changes how an element participates in layout; it does not change its underlying HTML meaning. A paragraph made display:flex remains a paragraph semantically.

Positioning modifies placement relative to a containing block or scroll container. Relative positioning keeps the element's original space while offsetting its painted position. Absolute positioning removes it from ordinary flow and uses a containing block, often the nearest positioned ancestor. Fixed positioning is often tied to the viewport but transformed ancestors can affect that behavior. Sticky positioning depends on a scroll container and an inset threshold.

Use position:relative on a card only when it intentionally establishes the containing block for an absolute badge. Keep the main article content in flow. A sticky section label needs an inset such as top:0 and sufficient scroll space. Avoid putting every element at exact pixel coordinates; content length and viewport width will change.

## Exercise 1: Predict whether relative positioning frees the original space.

It does not; the original layout space remains.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Turn a group of inline links into a block navigation list.

Display changes the arrangement without changing navigation semantics.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a card with an intentional positioned badge and flowing content.

Long body text expands the card while the badge stays in its reserved corner.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose an absolute label overlapping enlarged text.

Provide sufficient reserved space or return the label to normal flow.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Add a long paragraph and narrow the preview.

Content remains readable and the badge does not obscure it.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the containing block used by an absolute element.

Identify the actual ancestor that establishes it, rather than assuming it is always the viewport.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
