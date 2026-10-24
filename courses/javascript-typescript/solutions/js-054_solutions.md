# js-054: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A reusable chart component has an explicit input, output and lifecycle. It should not depend on a hidden global dataset or append another entire chart every time a caller updates it. A useful render contract specifies data shape, dimensions, identity, empty state and cleanup.

Responsive display is not the same as recomputing every data transformation on every resize. An SVG viewBox can scale an existing coordinate system to fit a container. More complex charts may need width-dependent tick density or label layout. Decide which parts change with available space and which analytical quantities remain invariant.

The reference renders into a caller-owned group and updates a keyed join. It checks that a second render does not duplicate marks and that an empty input produces a readable message. This is a foundation for dashboards whose views share state without sharing accidental DOM mutations.

Pass the container selection, data and size as arguments. Validate dimensions and records at the boundary. Compute scales from current input and update managed nodes. Keep the surrounding SVG and accessibility summary under clear ownership.

A ResizeObserver can detect actual container size, but it has a lifecycle and can trigger repeated callbacks. Disconnect it when the component is removed. The reference uses two explicit widths for deterministic acceptance; a real responsive integration should also be manually tested at narrow and wide browser sizes.

## Exercise 1: Predict mark count after two renders.

A component updates its owned nodes. Repeated calls should not accumulate entire charts.

**Expected:** It equals current record count, not the sum of all prior counts.

## Exercise 2: Change width while retaining data.

Responsive layout is a presentation transformation. It should not silently alter aggregation or records.

**Expected:** Geometry changes while values and identity remain stable.

## Exercise 3: Implement a reusable bar renderer.

A small contract makes the component testable outside a large dashboard. Avoid hidden globals for data and dimensions.

**Expected:** Explicit inputs, keyed marks and a documented empty state.

## Exercise 4: Diagnose duplicate SVG trees after resize.

Choose a single owner for the SVG root and reconcile its children. Cleanup is part of component behavior.

**Expected:** The update path creates new roots rather than updating an owned tree.

## Exercise 5: Render an empty dataset after nonempty data.

Empty-state behavior must work on updates, not just initial load. Check both transitions.

**Expected:** Stale marks disappear and the no-data message appears.

## Exercise 6: Plan real narrow-screen acceptance.

A scaled screenshot alone can conceal unreadable text. Inspect the actual interaction and label layout at the intended size.

**Expected:** Readable labels, no clipping, keyboard access and stable data meaning.
