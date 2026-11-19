# web-004: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-004.md`.

## Exercise 1: Resolve ../images/plot.svg from /notes/week1/page.html.

**Expected answer:** The resolved path is /notes/images/plot.svg on the same origin.

**Why:** The base directory is /notes/week1/; .. moves up to /notes/, then images/plot.svg is appended, and the scheme and host stay the same.

## Exercise 2: Replace vague link text with destination-specific wording.

**Expected evidence:** The link makes sense outside its surrounding sentence.

**Why:** People often navigate by a list of links, where text such as click here gives no destination.

## Exercise 3: Build a contents list that navigates to three local sections.

**Expected evidence:** Every fragment matches one unique section id and works with keyboard activation.

**Why:** A fragment link scrolls to the element whose id matches; a duplicate or missing id makes the target ambiguous or absent.

## Exercise 4: Diagnose a link whose fragment has no matching id.

**Expected answer:** The link has no intended target even if its visual style looks correct.

**Why:** Fragment matching is exact and case-sensitive, so a link can look correct and still have no target.

## Exercise 5: Distinguish a disabled action from an unavailable destination.

**Expected answer:** A button can be disabled; a meaningful alternative explanation should replace a dead link.

**Why:** Buttons have a disabled state that blocks activation, while links do not; an unavailable destination should be explained in text instead of left as a dead link.

## Exercise 6: Explain the difference between absolute, root-relative and document-relative paths.

**Expected answer:** Each has a distinct base and can resolve differently when the document moves.

**Why:** An absolute URL includes scheme and host, a root-relative path starts at the site root and a document-relative path depends on the current document's directory, so only the last one changes when the page moves.

## Reference comparison

Open `courses/web-development/solutions/web-004_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
