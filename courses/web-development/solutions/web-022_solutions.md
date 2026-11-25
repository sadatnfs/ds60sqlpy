# web-022: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-022.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict the layer winner for normal declarations.

**Expected answer:** A later declared layer outranks an earlier one before specificity is compared.

**Approach:** Compare the layer order declared in the first `@layer` statement first, and only compare specificity for declarations that share a layer.

**Why:** For normal declarations, a later layer beats an earlier one regardless of selector specificity.

**Plausible wrong approach:** Choosing the rule with the more specific selector fails because a later layer wins over an earlier one no matter how specific the earlier selector is.

**How to verify:** Give the base rule an id selector; the component color still wins, and the Styles panel strikes through the base declaration.

## Exercise 2: Move a component's rules into one named layer.

**Expected evidence:** Its styling responsibility is grouped and discoverable.

**Approach:** Gather the `.note` rule and its nested `&:hover` state into one `@layer components` block and delete the scattered copies.

**Why:** Grouping the rules by responsibility makes their priority predictable and easy to find.

**Plausible wrong approach:** Leaving the hover rule unlayered at the bottom of the file fails because it now outranks utilities and becomes impossible to override cleanly.

**How to verify:** Searching the stylesheet for `.note` finds one block, and hovering a note still underlines it.

## Exercise 3: Build a small layered stylesheet with base, component and utility rules.

**Expected evidence:** The intended overrides work without escalating ids or important flags.

**Approach:** Declare the order once, put element defaults in base, components in components, and single-purpose helpers such as `.text-muted` in utilities.

**Why:** Layer order resolves conflicts, so you do not need ids or !important to make a utility win.

**Plausible wrong approach:** Fixing an override by adding `!important` to a utility fails because important declarations reverse layer order and make later reasoning harder.

**How to verify:** Adding `.text-muted` to a note changes its color to #475569 with no `!important` and no id selector anywhere.

## Exercise 4: Diagnose an unlayered rule unexpectedly beating layered normal rules.

**Expected answer:** Unlayered normal author declarations have higher layer priority.

**Approach:** Search the stylesheet for rules outside any `@layer` block, especially late quick fixes, and move each into the layer that matches its role.

**Why:** Unlayered normal declarations beat all layered normal declarations, which surprises authors who expect source order to decide.

**Plausible wrong approach:** Raising the component selector's specificity fails because the unlayered rule wins before specificity is even compared.

**How to verify:** Once the quick fix lives in base, the component color appears and the Styles panel shows the unlayered rule gone.

## Exercise 5: Place the component under a different parent.

**Expected evidence:** Its behavior does not rely on an accidental deep ancestor selector.

**Approach:** Move the card's markup from the main column into an aside and check that every component style still applies in the new place.

**Why:** A selector tied to a deep ancestor chain breaks when the component moves, while a component class keeps working.

**Plausible wrong approach:** Writing selectors like `main section .card p` fails because the component then loses its styles the moment it moves outside that ancestry.

**How to verify:** The card renders identically inside the aside, and its matched rules list only component class selectors.

## Exercise 6: Explain why important declarations complicate layer reasoning.

**Expected answer:** Important layer ordering is reversed, so the normal ordering intuition no longer applies.

**Approach:** Recall that for important declarations the layer ranking flips, so an earlier layer's `!important` beats a later layer's `!important`.

**Why:** For important declarations the layer order reverses, so an earlier layer wins, the opposite of normal declarations.

**Plausible wrong approach:** Assuming important rules simply follow the normal later-wins order fails because base `!important` would then be expected to lose, which it does not.

**How to verify:** Mark the same property important in base and utilities; the base value wins, which matches the reversed order.

## Reference comparison

The reference reads the computed color of the text-muted paragraph and requires rgb(71, 85, 105), so it catches a utility layer declared too early or a component rule that still wins. It does not test the hover rule, layer placement of every rule or what happens under a different parent, so inspect the cascade in the Styles pane.

Open `courses/web-development/solutions/web-022_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
