# web-016: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-016.md`.

## Exercise 1: Explain why two 1fr tracks plus a gap are not two 50% widths plus a gap.

**Expected answer:** Fractional tracks divide the remaining space after the gap.

**Approach:** Subtract the gap from the container width first, then divide the remaining space by the total number of fr units.

**Why:** fr units share the space left after gaps and fixed tracks, so two 1fr tracks plus a 1rem gap are each half of the remaining width, not 50 percent of the container.

**Plausible wrong approach:** Using `50%` columns plus `gap: 1rem` fails because the columns alone already fill the container and the gap causes overflow.

**How to verify:** For a 600px container with a 1rem gap at 16px, each 1fr track measures 292px in the grid inspector.

## Exercise 2: Add a fourth card without new positional rules.

**Expected evidence:** Auto placement incorporates the item using the same layout contract.

**Approach:** Append a fourth card element to the container and let auto placement put it into the next available cell.

**Why:** Auto placement fills the next available cell, so the existing column definition decides where a new item goes.

**Plausible wrong approach:** Adding `grid-column` and `grid-row` values for each new card fails because the layout breaks when cards are added or removed.

**How to verify:** The new card appears in the next cell with no new CSS rules, and the grid overlay shows the same tracks.

## Exercise 3: Build an adaptive topic grid that survives a narrow container.

**Expected evidence:** Cards change column count while preserving reading order and avoiding page overflow.

**Approach:** Use `repeat(auto-fit, minmax(min(100%, 14rem), 1fr))` with a gap, and keep the cards in reading order in the source.

**Why:** minmax with min(100%, 14rem) lets each track shrink to the container width on narrow screens, and auto-fit chooses the column count from the available space.

**Plausible wrong approach:** Using `minmax(14rem, 1fr)` without `min()` fails because a container narrower than 14rem forces horizontal overflow.

**How to verify:** In a container 12rem wide, one column fills the space and the page shows no horizontal scrollbar.

## Exercise 4: Diagnose a long value widening a track.

**Expected answer:** Inspect minimum content sizing and use a deliberate minmax or wrapping policy.

**Approach:** Inspect the track sizes in the grid overlay and check whether a long value set the min-content width.

**Why:** A 1fr track has an automatic minimum equal to its min-content size, so minmax(0, 1fr) or wrapping is needed to stop one long value from widening it.

**Plausible wrong approach:** Adding `overflow: hidden` to the cell fails because the track is still sized by content and the hidden text is lost.

**How to verify:** After switching to `minmax(0, 1fr)` and wrapping, both tracks report equal widths in the overlay.

## Exercise 5: Test empty, one-card and seven-card collections.

**Expected evidence:** The layout remains coherent without a special case tied to three cards.

**Approach:** Render the grid with zero cards, one card and seven cards, checking both a wide and a narrow container.

**Why:** Intrinsic grid rules adapt to any item count, while rules written for exactly three cards break when content changes.

**Plausible wrong approach:** Tuning the layout for exactly three cards fails because a seventh card leaves an awkward final row that you never saw.

**How to verify:** The seven-card grid wraps into full rows plus one partial row, and the empty grid shows a message rather than a gap.

## Exercise 6: Explain auto-fit versus auto-fill at a high level.

**Expected answer:** Auto-fit can collapse empty repeated tracks; auto-fill preserves the generated track slots.

**Approach:** Compare one card in a wide container under `auto-fit` and under `auto-fill`, watching whether it stretches.

**Why:** auto-fill keeps empty tracks reserved, while auto-fit collapses empty tracks so the existing cards stretch to fill the row.

**Plausible wrong approach:** Treating the keywords as synonyms fails because with few items `auto-fill` keeps empty tracks and the card stays narrow.

**How to verify:** With one card, `auto-fit` stretches it across the row, while `auto-fill` keeps it at one track width.

## Reference comparison

Open `courses/web-development/solutions/web-016_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
