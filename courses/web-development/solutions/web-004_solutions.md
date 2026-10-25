# web-004: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A URL identifies a resource and can contain a scheme, host, path, query and fragment. A relative path is resolved against a base URL; it is not resolved against the author's mental picture of a folder. A fragment such as #methods identifies a location within the current document and does not require another document to exist. An anchor with href provides navigation semantics and keyboard behavior automatically.

Good link text tells a reader the destination or action. A page full of links named click here loses meaning when links are read as a list. A link navigates; a button changes application state or submits an action. Styling a paragraph blue does not create link behavior, and adding a click listener does not automatically provide keyboard support.

Use `href="#details"` with a unique `id="details"` for this offline lesson. A leading slash means a path from the origin root, while `../` moves one directory upward relative to the base path. Production external links may need a new-window notice and suitable rel values; do not open new tabs by default merely to keep a user on your site.

## Exercise 1: Resolve ../images/plot.svg from /notes/week1/page.html.

The resolved path is /notes/images/plot.svg on the same origin.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Replace vague link text with destination-specific wording.

The link makes sense outside its surrounding sentence.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a contents list that navigates to three local sections.

Every fragment matches one unique section id and works with keyboard activation.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a link whose fragment has no matching id.

The link has no intended target even if its visual style looks correct.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Distinguish a disabled action from an unavailable destination.

A button can be disabled; a meaningful alternative explanation should replace a dead link.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the difference between absolute, root-relative and document-relative paths.

Each has a distinct base and can resolve differently when the document moves.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
