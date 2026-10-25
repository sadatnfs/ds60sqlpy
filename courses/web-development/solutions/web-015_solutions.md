# web-015: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Flexbox distributes space among items primarily along one axis. The main axis follows flex-direction, while the cross axis is perpendicular. justify-content distributes available space along the main axis; align-items aligns items along the cross axis. The names do not permanently mean horizontal and vertical because direction can change.

Flexible items have a basis and rules for growing or shrinking. A row of long labels may overflow if wrapping is disabled or if an item's automatic minimum size prevents shrinking. `min-inline-size:0` is often useful for a flex child that must allow its text to wrap or truncate deliberately. Flexbox is a layout tool, not permission to reorder content into a confusing keyboard sequence.

Use display:flex, gap and flex-wrap:wrap for a simple responsive group. `flex: 1 1 12rem` gives an initial basis and permits growth and shrinkage. Set `align-items:stretch` when equal cross-axis size supports the component. Keep DOM order aligned with intended reading and focus order rather than using order to create a contradictory visual sequence.

## Exercise 1: Name the axes for flex-direction:column.

The main axis is vertical in the usual horizontal writing mode; the cross axis is horizontal.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add gap between navigation items without per-item margins.

Spacing is owned by the container and stays consistent when wrapping.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a wrapping navigation bar and flexible card row.

Long labels stay reachable at narrow widths and DOM order remains logical.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a flex child that refuses to shrink.

Inspect its minimum size, long content and flex-basis before forcing overflow hidden.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test one item, many items and a very long label.

The layout remains readable without relying on exactly three equal strings.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain when Flexbox fits better than Grid.

Use Flexbox for distributing items along one primary dimension; use Grid for explicit two-dimensional alignment.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
