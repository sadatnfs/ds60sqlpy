# web-022: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A stylesheet is easier to change when responsibilities are visible. Base rules describe document defaults, component rules describe reusable structures, and narrowly named utilities make deliberate local adjustments. These categories are a design choice, not a browser feature by themselves. Cascade layers let authors establish an explicit ordering among groups of declarations without continually increasing selector specificity.

For normal author declarations, later layers take priority over earlier layers, and unlayered normal declarations have priority over layered normal declarations. Important declarations reverse layer priority, which is one reason indiscriminate important usage makes reasoning harder. A good architecture keeps selectors understandable and limits the area a change can affect.

Declare the layer order once with `@layer base, components, utilities`. Put actual rules inside those layers. Keep component names tied to a useful responsibility such as lesson-card, not a visual accident such as left-blue-box. Test a component in more than one surrounding context to expose accidental ancestor dependencies.

## Exercise 1: Predict the layer winner for normal declarations.

A later declared layer outranks an earlier one before specificity is compared.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Move a component's rules into one named layer.

Its styling responsibility is grouped and discoverable.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a small layered stylesheet with base, component and utility rules.

The intended overrides work without escalating ids or important flags.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose an unlayered rule unexpectedly beating layered normal rules.

Unlayered normal author declarations have higher layer priority.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Place the component under a different parent.

Its behavior does not rely on an accidental deep ancestor selector.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why important declarations complicate layer reasoning.

Important layer ordering is reversed, so the normal ordering intuition no longer applies.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
