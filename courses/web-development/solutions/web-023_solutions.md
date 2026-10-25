# web-023: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Progressive enhancement starts from useful content and adds capabilities when the environment supports them. A document should communicate its core information before advanced styling or scripts run. This does not mean every application must offer identical features in every environment; it means essential requirements and fallbacks are deliberate rather than accidental.

Print is a different presentation context. Navigation controls that are useful on screen can waste space on paper, while a visible URL or document title may become more valuable. A print stylesheet can remove decoration, preserve contrast and avoid splitting small related blocks. It cannot guarantee the printer, paper size or user settings, so inspect the browser's print preview before making claims.

Use `@media print` for print-specific rules and `@supports` for a feature-dependent enhancement. Keep the base rule valid independently. Avoid hiding the actual article while removing navigation. `break-inside:avoid` is a request to the fragmentation system, not a promise that an arbitrarily large element fits on one page.

## Exercise 1: Identify content that must survive when scripts fail.

The page's primary information and basic navigation remain available.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a print rule that removes only irrelevant controls.

The article and its headings remain in print preview.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build printable study notes with a useful baseline layout.

Screen and print views preserve meaning with appropriate presentation.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a print rule that hides the main region.

Narrow the selector to navigation or actions instead of the content container.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Inspect multiple pages of print preview.

Headings, tables and long blocks remain legible across page breaks.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what a feature query proves and what it does not.

It detects supported syntax, not performance, usability or correctness of the whole component.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
