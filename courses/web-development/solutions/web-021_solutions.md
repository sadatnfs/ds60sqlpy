# web-021: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-021.md`.

## Exercise 1: Explain why two cards on the same viewport can use different layouts.

**Expected answer:** Their query containers can have different widths.

**Why:** Container queries test the nearest query container, so the same component can match in one slot and not in another.

## Exercise 2: Add a container wrapper around a reusable card.

**Expected evidence:** The card has an explicit local sizing context.

**Why:** An element cannot query its own size, so the wrapper must establish the container that the card's rules test.

## Exercise 3: Render the same component in wide and narrow slots.

**Expected evidence:** Each instance adapts independently while preserving its content.

**Why:** Each instance evaluates the query against its own container, so they adapt independently.

## Exercise 4: Diagnose a query that never matches because no ancestor is eligible.

**Expected answer:** Inspect container-type and the relevant ancestor relationship.

**Why:** A container query only matches when an ancestor establishes size containment; without one, the query never applies.

## Exercise 5: Disable the query and inspect the fallback.

**Expected evidence:** The baseline stacked component remains usable.

**Why:** The baseline rules outside the query must work on their own, because the query is an enhancement.

## Exercise 6: Choose between a viewport query and a container query for a sidebar card.

**Expected answer:** A container query fits a component whose available space depends on placement.

**Why:** A card in a sidebar gets the sidebar's width, so a container query describes its real space better than the viewport.

## Reference comparison

Open `courses/web-development/solutions/web-021_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
