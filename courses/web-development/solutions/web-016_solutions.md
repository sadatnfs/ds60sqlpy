# web-016: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-016.md`.

## Exercise 1: Explain why two 1fr tracks plus a gap are not two 50% widths plus a gap.

**Expected answer:** Fractional tracks divide the remaining space after the gap.

**Why:** fr units share the space left after gaps and fixed tracks, so two 1fr tracks plus a 1rem gap are each half of the remaining width, not 50 percent of the container.

## Exercise 2: Add a fourth card without new positional rules.

**Expected evidence:** Auto placement incorporates the item using the same layout contract.

**Why:** Auto placement fills the next available cell, so the existing column definition decides where a new item goes.

## Exercise 3: Build an adaptive topic grid that survives a narrow container.

**Expected evidence:** Cards change column count while preserving reading order and avoiding page overflow.

**Why:** minmax with min(100%, 14rem) lets each track shrink to the container width on narrow screens, and auto-fit chooses the column count from the available space.

## Exercise 4: Diagnose a long value widening a track.

**Expected answer:** Inspect minimum content sizing and use a deliberate minmax or wrapping policy.

**Why:** A 1fr track has an automatic minimum equal to its min-content size, so minmax(0, 1fr) or wrapping is needed to stop one long value from widening it.

## Exercise 5: Test empty, one-card and seven-card collections.

**Expected evidence:** The layout remains coherent without a special case tied to three cards.

**Why:** Intrinsic grid rules adapt to any item count, while rules written for exactly three cards break when content changes.

## Exercise 6: Explain auto-fit versus auto-fill at a high level.

**Expected answer:** Auto-fit can collapse empty repeated tracks; auto-fill preserves the generated track slots.

**Why:** auto-fill keeps empty tracks reserved, while auto-fit collapses empty tracks so the existing cards stretch to fill the row.

## Reference comparison

Open `courses/web-development/solutions/web-016_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
