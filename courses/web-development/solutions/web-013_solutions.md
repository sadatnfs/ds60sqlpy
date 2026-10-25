# web-013: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Color can group information, but it cannot be the only carrier of an essential distinction. A failed status should have words or an icon with an accessible name as well as a color. Contrast is the difference in luminance that makes foreground content distinguishable from its background. A pleasing palette does not automatically provide readable text or usable controls. Test the actual foreground-background pair in each state, including hover, focus, disabled and error.

Focus identifies the element receiving keyboard input. Removing the browser's outline without a replacement makes navigation difficult or impossible for many users. The focus-visible pseudo-class lets the browser apply its heuristics for when focus needs a visible indicator. A control can also require an adequately sized target and enough spacing from neighboring controls.

Define a small set of tokens for text, background, accent and borders, then inspect their combinations. Use an outline with an offset so it is not hidden by the border. A status element can contain the word Ready or Needs attention; color reinforces that label. Prefer explicit text to a legend that a reader must memorize.

## Exercise 1: Identify the missing information in a red-only error dot.

The user needs a textual error meaning and a useful recovery action.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a focus-visible style without removing focus support.

Keyboard focus is visibly distinguishable from hover.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build status cards whose meaning does not depend on color.

Each card contains a clear label, readable text and visible interactive focus.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a focus ring clipped by overflow.

Inspect the ancestor clipping boundary and provide space or a different visible indicator.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Inspect the page in a forced-colors or high-contrast setting.

Native boundaries and meaningful labels remain available; document actual browser behavior.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why one palette check does not qualify every interaction state.

Backgrounds and foregrounds can change per state, so each important combination needs review.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
