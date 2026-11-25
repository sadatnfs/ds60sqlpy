# web-005: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-005.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Choose a list type for steps and an unordered tool collection.

**Expected answer:** Steps use ol; interchangeable peer tools use ul.

**Approach:** Ask whether reordering the items would change the meaning; steps fail that test and get `ol`, while peer tools pass it and get `ul`.

**Why:** An ordered list communicates sequence, so assistive technology announces item numbers; an unordered list signals interchangeable items.

**Plausible wrong approach:** Choosing `ol` for tools because numbering looks tidy fails because it tells readers the order matters when it does not.

**How to verify:** The steps list exposes `ol` with three ordered `li` items and the tools list exposes `ul` in the Elements panel.

## Exercise 2: Add two vocabulary terms with definitions.

**Expected evidence:** A dl contains paired dt and dd elements.

**Approach:** Write a `dl` and add each term as a `dt` followed directly by its `dd` definition.

**Why:** A description list associates each dt with its dd, so the relationship is expressed by markup instead of bold text.

**Plausible wrong approach:** Using two paragraphs with bold terms fails because the pairing becomes visual only, and no element ties each definition to its term.

**How to verify:** `document.querySelectorAll('dl > dt').length` and `dl > dd` both return 2, alternating in the tree.

## Exercise 3: Build a study checklist with a code example and glossary.

**Expected evidence:** The page exposes list, code and definition structures without relying on spacing.

**Approach:** Combine an `ol` checklist, a `pre` with `code` whose angle brackets are escaped, and a `dl` glossary inside one `main`.

**Why:** Each element tells browsers and assistive technology what the content is, so the page stays meaningful without spacing or color.

**Plausible wrong approach:** Pasting raw `<p>` inside the `code` block fails because the parser creates a real paragraph and the example text disappears.

**How to verify:** The preview shows literal angle brackets in the code region and the tree contains no element created from the example text.

## Exercise 4: Repair a nested list placed as a sibling of its parent item.

**Expected evidence:** The nested list belongs inside the associated li.

**Approach:** Move the nested `ul` inside the `li` it elaborates, before that `li` closes.

**Why:** ul and ol may contain only li children, so a sublist must sit inside an item to show that it belongs to that step.

**Plausible wrong approach:** Fixing the indentation alone fails because whitespace does not change parent and child relationships in the parsed tree.

**How to verify:** `document.querySelector('ul > ul')` returns null after the repair and the inner list's parent is an `li`.

## Exercise 5: Test a long code line in a narrow preview.

**Expected evidence:** The code region can scroll without making the entire page horizontally overflow.

**Approach:** Give `pre` an `overflow-x: auto` rule so the long line scrolls inside its own box at narrow widths.

**Why:** overflow-x: auto on the code container creates a local scroll area, so the rest of the page keeps its width.

**Plausible wrong approach:** Applying `white-space: nowrap` to the whole body fails because every paragraph then overflows, widening the entire page.

**How to verify:** At the narrow viewport preset, the page has no horizontal scrollbar while the code box shows its own scrollbar.

## Exercise 6: Explain the difference between preserving whitespace and preserving meaning.

**Expected answer:** Pre preserves formatting; semantic elements additionally communicate content roles.

**Approach:** Contrast `pre`, which keeps spaces and line breaks, with semantic elements such as `ol` or `code`, which say what the content is.

**Why:** pre only preserves spaces and line breaks; semantic elements state what the content is, which whitespace alone cannot.

**Plausible wrong approach:** Building a list from `pre` and spaces fails because the text lines up visually but exposes no list or item to assistive technology.

**How to verify:** A list written in `pre` shows no list role in the accessibility tree, while the `ol` version reports its item count.

## Reference comparison

The reference counts dt elements inside a dl and requires two, so it catches a glossary written as paragraphs or a missing term. It does not verify that each dt has a dd, that the nested tools list sits inside its parent li or that code was escaped, so inspect the tree for those.

Open `courses/web-development/solutions/web-005_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
