# web-023: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-023.md`.

## Exercise 1: Identify content that must survive when scripts fail.

**Expected answer:** The page's primary information and basic navigation remain available.

**Why:** Content and links in the HTML remain available when scripts fail, which is the baseline progressive enhancement protects.

## Exercise 2: Add a print rule that removes only irrelevant controls.

**Expected evidence:** The article and its headings remain in print preview.

**Why:** A print view keeps the article and headings because the reader wants the content, not controls that cannot work on paper.

## Exercise 3: Build printable study notes with a useful baseline layout.

**Expected evidence:** Screen and print views preserve meaning with appropriate presentation.

**Why:** A content-first baseline keeps meaning in both media, while each media query only changes presentation.

## Exercise 4: Diagnose a print rule that hides the main region.

**Expected answer:** Narrow the selector to navigation or actions instead of the content container.

**Why:** display: none on a container removes everything inside it, so the rule must target the controls themselves.

## Exercise 5: Inspect multiple pages of print preview.

**Expected evidence:** Headings, tables and long blocks remain legible across page breaks.

**Why:** Page breaks can split tables and headings from their content, which only appears across multiple pages.

## Exercise 6: Explain what a feature query proves and what it does not.

**Expected answer:** It detects supported syntax, not performance, usability or correctness of the whole component.

**Why:** A feature query checks whether the browser parses a property and value, not whether the result is fast, accessible or correct.

## Reference comparison

Open `courses/web-development/solutions/web-023_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
