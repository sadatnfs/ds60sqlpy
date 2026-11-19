# web-003: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-003.md`.

## Exercise 1: Draw the heading outline of the first example.

**Expected answer:** Study notes contains HTML as one second-level section.

**Why:** Heading levels express nesting: an h2 inside the h1 topic is a subsection, so the outline follows the numbers, not the font sizes.

## Exercise 2: Add a sibling CSS section at the correct level.

**Expected evidence:** CSS and HTML both use h2 because they have the same parent topic.

**Why:** Topics that share a parent share a heading level; an h3 would make CSS a subsection of HTML.

## Exercise 3: Build a study page with landmarks and a working skip link.

**Expected evidence:** Header, labeled navigation, one main and footer have meaningful content; the skip target exists.

**Why:** Landmarks let assistive technology jump between regions, and the skip link lets keyboard users bypass repeated navigation; both depend on the target id existing exactly once.

## Exercise 4: Replace a heading used only for large text with an appropriate element.

**Expected evidence:** A visual callout uses CSS without corrupting the document outline.

**Why:** Headings build the document outline that screen-reader users navigate, so a decorative heading inserts a false section.

## Exercise 5: Check the document with CSS disabled or unavailable.

**Expected evidence:** The reading order and heading relationships remain coherent.

**Why:** Source order is the reading and focus order for most users, so a page that only makes sense visually hides a structural problem.

## Exercise 6: Explain when a div is more appropriate than section.

**Expected answer:** Use a generic container when grouping does not introduce a meaningful headed section.

**Why:** section represents a thematic group that normally has a heading; div carries no meaning and is right for grouping that exists only for styling.

## Reference comparison

Open `courses/web-development/solutions/web-003_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
