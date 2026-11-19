# web-005: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-005.md`.

## Exercise 1: Choose a list type for steps and an unordered tool collection.

**Expected answer:** Steps use ol; interchangeable peer tools use ul.

**Why:** An ordered list communicates sequence, so assistive technology announces item numbers; an unordered list signals interchangeable items.

## Exercise 2: Add two vocabulary terms with definitions.

**Expected evidence:** A dl contains paired dt and dd elements.

**Why:** A description list associates each dt with its dd, so the relationship is expressed by markup instead of bold text.

## Exercise 3: Build a study checklist with a code example and glossary.

**Expected evidence:** The page exposes list, code and definition structures without relying on spacing.

**Why:** Each element tells browsers and assistive technology what the content is, so the page stays meaningful without spacing or color.

## Exercise 4: Repair a nested list placed as a sibling of its parent item.

**Expected evidence:** The nested list belongs inside the associated li.

**Why:** ul and ol may contain only li children, so a sublist must sit inside an item to show that it belongs to that step.

## Exercise 5: Test a long code line in a narrow preview.

**Expected evidence:** The code region can scroll without making the entire page horizontally overflow.

**Why:** overflow-x: auto on the code container creates a local scroll area, so the rest of the page keeps its width.

## Exercise 6: Explain the difference between preserving whitespace and preserving meaning.

**Expected answer:** Pre preserves formatting; semantic elements additionally communicate content roles.

**Why:** pre only preserves spaces and line breaks; semantic elements state what the content is, which whitespace alone cannot.

## Reference comparison

Open `courses/web-development/solutions/web-005_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
