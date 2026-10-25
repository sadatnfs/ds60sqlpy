# web-021: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A media query responds to the viewport or device environment. A container query can respond to an ancestor container's size, which is useful when the same component appears in a wide article and a narrow sidebar on the same page. The component should adapt to the space it receives instead of assuming it always spans the viewport.

Size containment changes how a container participates in sizing. Declare it deliberately on an appropriate wrapper, not on every element. A size query targets an eligible ancestor, not the queried element itself. Keep a useful base layout so the component remains readable in environments where the query is unsupported or never matches.

Set `container-type:inline-size` on a wrapper, optionally with a container-name. Inside `@container`, adjust the descendant component when its wrapper is wide enough. Prefer logical dimensions so the design does not unnecessarily assume a writing direction. This chapter demonstrates progressive enhancement; the unqueried stacked card remains functional.

## Exercise 1: Explain why two cards on the same viewport can use different layouts.

Their query containers can have different widths.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a container wrapper around a reusable card.

The card has an explicit local sizing context.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Render the same component in wide and narrow slots.

Each instance adapts independently while preserving its content.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a query that never matches because no ancestor is eligible.

Inspect container-type and the relevant ancestor relationship.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Disable the query and inspect the fallback.

The baseline stacked component remains usable.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Choose between a viewport query and a container query for a sidebar card.

A container query fits a component whose available space depends on placement.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
