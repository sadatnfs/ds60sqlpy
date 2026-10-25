# web-016: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Grid arranges items along rows and columns. A track is the space between two adjacent grid lines. Fractional fr units share remaining space after fixed sizes and gaps have been considered. They are not a fixed percentage of the full container. An item's minimum content contribution can still affect track size, which explains why a long unbroken value may widen an apparently equal grid.

Grid is useful when rows and columns must align across a collection. An auto-fit repeat with minmax can create as many columns as fit a preferred minimum, then distribute remaining room. The minimum must still fit a narrow viewport. A layout should adapt to its content, not depend on one device model or a fixed card count.

Use `grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr))` for a resilient card collection. The inner min permits a track to fit a container narrower than the preferred minimum. `gap` adds separation without changing source order. Named grid areas are useful for a page shell, but the source order must remain understandable when the layout collapses.

## Exercise 1: Explain why two 1fr tracks plus a gap are not two 50% widths plus a gap.

Fractional tracks divide the remaining space after the gap.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a fourth card without new positional rules.

Auto placement incorporates the item using the same layout contract.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build an adaptive topic grid that survives a narrow container.

Cards change column count while preserving reading order and avoiding page overflow.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a long value widening a track.

Inspect minimum content sizing and use a deliberate minmax or wrapping policy.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test empty, one-card and seven-card collections.

The layout remains coherent without a special case tied to three cards.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain auto-fit versus auto-fill at a high level.

Auto-fit can collapse empty repeated tracks; auto-fill preserves the generated track slots.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
