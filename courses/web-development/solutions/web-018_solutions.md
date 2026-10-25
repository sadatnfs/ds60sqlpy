# web-018: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A design token names a recurring design decision such as a spacing step, text color or border radius. CSS custom properties store values that participate in the cascade and can be scoped to a component. A variable name should communicate its purpose, such as --surface or --space-small, rather than merely its current value. That allows the value to change while the role remains stable.

Custom properties are resolved where they are used and usually inherit. A card can override a small set of tokens while retaining the same component rules. A fallback in var supplies a value when a variable is missing or invalid in the relevant way, but a custom property can still produce an invalid declaration at computed-value time. Test the final computed result instead of assuming any string is suitable for any property.

Define shared defaults at :root and override them on a component class. `background:var(--surface,white)` uses the current scope's value. Keep semantic text labels independent of theme color. A theme change must preserve contrast and focus behavior, not merely update an accent swatch.

## Exercise 1: Predict which card inherits a scoped token override.

Only the element with the override and its relevant descendants use that scope.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Replace repeated spacing literals with a semantic token.

A deliberate single token change updates the related spacing.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build two themed cards using one component rule.

The variants preserve content labels, contrast and focus while sharing structure.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a custom property used with an incompatible value.

Inspect the final property and computed-value validity, not only the variable's existence.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Remove an optional variable and inspect its fallback.

The component remains usable with its declared fallback.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain a token name that survives a palette change.

A role such as --error-text is more durable than a name tied only to a particular red value.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
