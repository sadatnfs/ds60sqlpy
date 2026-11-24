# web-023: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-023.md`.

## Exercise 1: Identify content that must survive when scripts fail.

**Expected answer:** The page's primary information and basic navigation remain available.

**Approach:** List what a reader came for, such as the article text, headings and plain links, and mark which pieces must work without scripts or styles.

**Why:** Content and links in the HTML remain available when scripts fail, which is the baseline progressive enhancement protects.

**Plausible wrong approach:** Naming the animated menu or the filter widget as essential fails because those enhancements depend on scripts that may never run.

**How to verify:** Disable JavaScript in developer tools; the article and its links are still present and readable in order.

## Exercise 2: Add a print rule that removes only irrelevant controls.

**Expected evidence:** The article and its headings remain in print preview.

**Approach:** Inside `@media print`, hide only `nav` and `button`, and reset the body to black text on a white background.

**Why:** A print view keeps the article and headings because the reader wants the content, not controls that cannot work on paper.

**Plausible wrong approach:** Hiding a wrapper that contains both navigation and the article fails because the descendants, including the content, disappear in print as well.

**How to verify:** Print preview shows the article heading and paragraphs while navigation and buttons are gone.

## Exercise 3: Build printable study notes with a useful baseline layout.

**Expected evidence:** Screen and print views preserve meaning with appropriate presentation.

**Approach:** Start from a block baseline for notes, add a Grid layout inside `@supports (display: grid)`, then add a print rule that removes controls only.

**Why:** A content-first baseline keeps meaning in both media, while each media query only changes presentation.

**Plausible wrong approach:** Putting the only layout inside the `@supports` block with no block baseline fails because unsupported environments get no readable structure at all.

**How to verify:** Removing the `@supports` block leaves notes readable in one column, and print preview keeps every heading.

## Exercise 4: Diagnose a print rule that hides the main region.

**Expected answer:** Narrow the selector to navigation or actions instead of the content container.

**Approach:** Inspect which element the print selector matches and check whether the main content is its descendant.

**Why:** display: none on a container removes everything inside it, so the rule must target the controls themselves.

**Plausible wrong approach:** Adding `display: block` to `main` inside the print rule fails because a hidden ancestor still hides every child.

**How to verify:** After narrowing the selector to `nav`, print preview shows the main region on the first page.

## Exercise 5: Inspect multiple pages of print preview.

**Expected evidence:** Headings, tables and long blocks remain legible across page breaks.

**Approach:** Scroll through every page of print preview and read the headings, table rows and long code blocks at each page break.

**Why:** Page breaks can split tables and headings from their content, which only appears across multiple pages.

**Plausible wrong approach:** Applying `break-inside: avoid` to the whole article fails because an element taller than a page must still split somewhere.

**How to verify:** Each page starts with readable content, and no heading sits alone at the bottom of a page.

## Exercise 6: Explain what a feature query proves and what it does not.

**Expected answer:** It detects supported syntax, not performance, usability or correctness of the whole component.

**Approach:** Read the `@supports` condition as a parser check: the browser reports whether it understands that property and value pair.

**Why:** A feature query checks whether the browser parses a property and value, not whether the result is fast, accessible or correct.

**Plausible wrong approach:** Treating a matched feature query as proof that the layout works well fails because supported syntax can still overflow or misorder content.

**How to verify:** A grid inside a matched `@supports` block can still overflow at narrow width, which you see only by resizing.

## Reference comparison

Open `courses/web-development/solutions/web-023_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
