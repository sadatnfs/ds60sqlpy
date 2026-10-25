# web-024: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A portal combines structure, navigation and repeated components around a user goal. Begin with the tasks: finding a topic, understanding prerequisites, choosing an action and reading progress. The information architecture groups content so those tasks are discoverable. A beautiful collection of cards is not enough if every label is vague or the reading order hides the main choice.

This milestone integrates the earlier mechanisms without requiring a framework. Semantic headings establish the outline, native links provide navigation, Grid or Flexbox distributes cards, and tokens maintain consistent spacing and color. Progress labels remain textual. The project uses synthetic data and does not claim persistent accounts or a working backend.

Write acceptance criteria before styling: one main region, descriptive page title, reachable navigation, distinct card headings, no color-only status, a narrow-width layout and a usable zoomed view. Implement the smallest coherent page, then audit the settled state at multiple widths. Keep appearance checks separate from structural checks because each can pass while the other fails.

## Exercise 1: Write three learner tasks before drawing the interface.

Find a topic, assess its prerequisites and choose a clear next action.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Define a small token set for the page.

Spacing, text and surface choices are consistent and named by role.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a complete offline portal with three paths and local destinations.

All cards, navigation and headings are meaningful, keyboard reachable and responsive.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Audit one deliberately vague link and one broken fragment.

Replace the vague label and repair the target relationship.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Review narrow width, zoom, keyboard and print behavior.

Retain observations for each surface instead of claiming a universal pass from one screenshot.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the portal's remaining backend requirements.

Persistent identity, saved progress and authorization need a server and storage contract beyond this static page.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
