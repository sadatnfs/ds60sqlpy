# web-022: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-022.md`.

## Exercise 1: Predict the layer winner for normal declarations.

**Expected answer:** A later declared layer outranks an earlier one before specificity is compared.

**Why:** For normal declarations, a later layer beats an earlier one regardless of selector specificity.

## Exercise 2: Move a component's rules into one named layer.

**Expected evidence:** Its styling responsibility is grouped and discoverable.

**Why:** Grouping the rules by responsibility makes their priority predictable and easy to find.

## Exercise 3: Build a small layered stylesheet with base, component and utility rules.

**Expected evidence:** The intended overrides work without escalating ids or important flags.

**Why:** Layer order resolves conflicts, so you do not need ids or !important to make a utility win.

## Exercise 4: Diagnose an unlayered rule unexpectedly beating layered normal rules.

**Expected answer:** Unlayered normal author declarations have higher layer priority.

**Why:** Unlayered normal declarations beat all layered normal declarations, which surprises authors who expect source order to decide.

## Exercise 5: Place the component under a different parent.

**Expected evidence:** Its behavior does not rely on an accidental deep ancestor selector.

**Why:** A selector tied to a deep ancestor chain breaks when the component moves, while a component class keeps working.

## Exercise 6: Explain why important declarations complicate layer reasoning.

**Expected answer:** Important layer ordering is reversed, so the normal ordering intuition no longer applies.

**Why:** For important declarations the layer order reverses, so an earlier layer wins, the opposite of normal declarations.

## Reference comparison

Open `courses/web-development/solutions/web-022_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
