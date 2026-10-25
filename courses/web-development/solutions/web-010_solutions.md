# web-010: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A CSS rule has a selector and a declaration block. The selector chooses elements; each declaration sets a property to a value. Several rules can match the same element. The cascade resolves conflicts using origin, importance, layer order, specificity, scoping proximity where applicable and source order. Specificity is not the entire algorithm. A later rule wins only after the earlier priorities tie.

Inheritance is another mechanism: some properties, such as text color, naturally pass from a parent to children unless overridden. Other properties, such as margins, normally do not. A value inherited from a parent does not beat a declaration directly targeting the child just because the parent selector is more specific. Browser developer tools reveal which rule won and which declaration was crossed out.

Start with low-specificity class selectors for reusable components. `.note` targets a class, `#summary` targets one id, and `p` targets an element type. `color: #17324d` is a declaration. Use the computed-style view to inspect the resolved value. Avoid adding important flags repeatedly to fight a conflict whose origin you have not identified.

## Exercise 1: Predict the winning color in the second example.

The later equally specific declaration wins.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Move a shared text color to a parent and inspect inheritance.

Children inherit it unless a direct declaration overrides it.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Style two note cards using one low-specificity class.

Both cards share styling without duplicate ids or inline declarations.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a crossed-out declaration in developer tools.

Identify the winning rule and the cascade reason rather than guessing.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Add a child color rule under a highly specific parent selector.

A direct declaration on the child overrides an otherwise inherited color.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why specificity alone does not describe the cascade.

Origin, importance and layer ordering can be decided before selector specificity.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
