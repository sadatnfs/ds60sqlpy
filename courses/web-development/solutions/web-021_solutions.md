# web-021: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-021.md`.

## Exercise 1: Explain why two cards on the same viewport can use different layouts.

**Expected answer:** Their query containers can have different widths.

**Approach:** Identify the query container for each card and compare the inline size of those two wrappers, not the width of the browser window.

**Why:** Container queries test the nearest query container, so the same component can match in one slot and not in another.

**Plausible wrong approach:** Saying both cards must match because they share one viewport fails, since `@container` never reads the viewport width at all.

**How to verify:** Inspect each `.slot`; the wider one shows a matched container rule while the narrower one shows the same rule unmatched.

## Exercise 2: Add a container wrapper around a reusable card.

**Expected evidence:** The card has an explicit local sizing context.

**Approach:** Wrap the card in an element such as `.slot`, give that wrapper `container-type: inline-size`, and keep the card's own grid rule as the stacked baseline.

**Why:** An element cannot query its own size, so the wrapper must establish the container that the card's rules test.

**Plausible wrong approach:** Adding `container-type` to the card itself fails because a query only looks at ancestors, so the card cannot change its own columns.

**How to verify:** The Elements panel shows a container badge on `.slot`, and the card becomes a descendant of that badge.

## Exercise 3: Render the same component in wide and narrow slots.

**Expected evidence:** Each instance adapts independently while preserving its content.

**Approach:** Place one slot in a wide main column and one in a narrow sidebar, using the same card markup and a single `@container` rule.

**Why:** Each instance evaluates the query against its own container, so they adapt independently.

**Plausible wrong approach:** Writing separate classes such as `.card-wide` and `.card-narrow` fails because each placement then needs manual edits whenever the layout around it changes.

**How to verify:** Narrow the main column until it crosses 28rem and only that card switches layout while the sidebar card stays stacked.

## Exercise 4: Diagnose a query that never matches because no ancestor is eligible.

**Expected answer:** Inspect container-type and the relevant ancestor relationship.

**Approach:** Walk up from the card to the first ancestor with a non-normal `container-type` and confirm the query condition uses an axis it contains.

**Why:** A container query only matches when an ancestor establishes size containment; without one, the query never applies.

**Plausible wrong approach:** Using a `block-size` condition with `container-type: inline-size` fails because that container only exposes its inline dimension to queries.

**How to verify:** After adding containment to the right ancestor, the Styles panel lists the container rule as matched at the wide size.

## Exercise 5: Disable the query and inspect the fallback.

**Expected evidence:** The baseline stacked component remains usable.

**Approach:** Comment out the whole `@container` block and read the card at wide and narrow widths with only the baseline grid rule active.

**Why:** The baseline rules outside the query must work on their own, because the query is an enhancement.

**Plausible wrong approach:** Hiding the image or text by default and revealing it in the query fails because readers lose content wherever the query does not match.

**How to verify:** Without the query, the image, heading and text all appear in one readable stacked column at every width.

## Exercise 6: Choose between a viewport query and a container query for a sidebar card.

**Expected answer:** A container query fits a component whose available space depends on placement.

**Approach:** Decide which measurement controls the card: the window for page-level structure, or the slot the card happens to occupy for a reusable component.

**Why:** A card in a sidebar gets the sidebar's width, so a container query describes its real space better than the viewport.

**Plausible wrong approach:** Using a viewport breakpoint for the sidebar card fails because a wide screen can still give the sidebar too little room for two columns.

**How to verify:** On a wide screen with a narrow sidebar, the container version stays stacked while a viewport version would squeeze two columns.

## Reference comparison

Open `courses/web-development/solutions/web-021_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
