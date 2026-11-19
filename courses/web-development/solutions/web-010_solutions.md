# web-010: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-010.md`.

## Exercise 1: Predict the winning color in the second example.

**Expected answer:** The later equally specific declaration wins.

**Why:** When origin, importance, layer and specificity are equal, the declaration that appears later in the source wins.

## Exercise 2: Move a shared text color to a parent and inspect inheritance.

**Expected evidence:** Children inherit it unless a direct declaration overrides it.

**Why:** color is inherited, so descendants use the parent's value unless they have a declaration of their own.

## Exercise 3: Style two note cards using one low-specificity class.

**Expected evidence:** Both cards share styling without duplicate ids or inline declarations.

**Why:** A single class has low specificity and is reusable, so later or more specific rules can still adjust one card.

## Exercise 4: Diagnose a crossed-out declaration in developer tools.

**Expected answer:** Identify the winning rule and the cascade reason rather than guessing.

**Why:** Developer tools strike through declarations that lost the cascade, and the winning rule reveals the reason: importance, layer, specificity or order.

## Exercise 5: Add a child color rule under a highly specific parent selector.

**Expected evidence:** A direct declaration on the child overrides an otherwise inherited color.

**Why:** Inheritance only supplies a value when an element has none of its own, so any declaration that matches the child beats an inherited value, whatever the parent selector's specificity.

## Exercise 6: Explain why specificity alone does not describe the cascade.

**Expected answer:** Origin, importance and layer ordering can be decided before selector specificity.

**Why:** The cascade compares origin and importance, then cascade layers, and only then specificity and order, so a simple selector in a later layer can still win.

## Reference comparison

Open `courses/web-development/solutions/web-010_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
