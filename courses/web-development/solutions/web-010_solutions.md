# web-010: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-010.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict the winning color in the second example.

**Expected answer:** The later equally specific declaration wins.

**Approach:** Confirm both rules use the same selector, `.note`, so specificity ties and the later declaration in source order wins.

**Why:** When origin, importance, layer and specificity are equal, the declaration that appears later in the source wins.

**Plausible wrong approach:** Choosing blue because it came first fails because the cascade breaks a specificity tie with the last declaration, not the first.

**How to verify:** The Computed panel for a `.note` element reports `rgb(139, 0, 0)`, which is dark red, for `color`.

## Exercise 2: Move a shared text color to a parent and inspect inheritance.

**Expected evidence:** Children inherit it unless a direct declaration overrides it.

**Approach:** Move `color: #17324d` from the cards to their shared parent and let the cards inherit it.

**Why:** color is inherited, so descendants use the parent's value unless they have a declaration of their own.

**Plausible wrong approach:** Expecting `padding` to inherit the same way fails because padding is not an inherited property.

**How to verify:** Each child shows the color as inherited from the parent in the Computed panel, while its padding stays at its own value.

## Exercise 3: Style two note cards using one low-specificity class.

**Expected evidence:** Both cards share styling without duplicate ids or inline declarations.

**Approach:** Write one `.note` rule and add `class="note"` to both cards instead of styling each card separately.

**Why:** A single class has low specificity and is reusable, so later or more specific rules can still adjust one card.

**Plausible wrong approach:** Styling `#card1` and `#card2` with duplicate rules fails because any change must be made twice and specificity rises.

**How to verify:** Changing one value in the `.note` rule updates both cards at once, and the source contains no `style` attributes.

## Exercise 4: Diagnose a crossed-out declaration in developer tools.

**Expected answer:** Identify the winning rule and the cascade reason rather than guessing.

**Approach:** Click the crossed-out declaration in the Styles panel and trace upward to the rule that won, noting its selector and origin.

**Why:** Developer tools strike through declarations that lost the cascade, and the winning rule reveals the reason: importance, layer, specificity or order.

**Plausible wrong approach:** Adding `!important` to the losing declaration fails because it hides the conflict and makes the next override harder.

**How to verify:** You can name the winning selector and the reason (specificity, order or importance) shown by developer tools.

## Exercise 5: Add a child color rule under a highly specific parent selector.

**Expected evidence:** A direct declaration on the child overrides an otherwise inherited color.

**Approach:** Give the child its own `color` declaration with a simple class selector, even though the parent rule is very specific.

**Why:** Inheritance only supplies a value when an element has none of its own, so any declaration that matches the child beats an inherited value, whatever the parent selector's specificity.

**Plausible wrong approach:** Raising the child's selector specificity to beat the parent fails because inherited values never compete with direct declarations by specificity.

**How to verify:** The child shows its own color in Computed while the parent keeps the highly specific value.

## Exercise 6: Explain why specificity alone does not describe the cascade.

**Expected answer:** Origin, importance and layer ordering can be decided before selector specificity.

**Approach:** List the cascade checks in order: origin and importance, then layers, then specificity, then source order.

**Why:** The cascade compares origin and importance, then cascade layers, and only then specificity and order, so a simple selector in a later layer can still win.

**Plausible wrong approach:** Saying the more specific selector always wins fails because an `!important` declaration of lower specificity beats a normal one.

**How to verify:** A `.note { color: green !important; }` rule overrides `#summary { color: navy; }` in the preview.

## Reference comparison

The reference reads the computed padding of the first note and requires 16px, so it catches a missing rule or a selector that does not match the class. It does not compare colors, test inheritance or show which declaration was overridden, so use the Styles pane to compare those decisions.

Open `courses/web-development/solutions/web-010_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
