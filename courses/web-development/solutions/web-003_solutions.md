# web-003: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-003.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Draw the heading outline of the first example.

**Expected answer:** Study notes contains HTML as one second-level section.

**Approach:** List each heading with its level in source order and indent each one under the nearest earlier heading of a lower number.

**Why:** Heading levels express nesting: an h2 inside the h1 topic is a subsection, so the outline follows the numbers, not the font sizes.

**Plausible wrong approach:** Reading the `section` element as the source of rank fails because the outline is defined by heading levels, not by how many sections wrap them.

**How to verify:** Your outline shows Study notes at level 1 and HTML at level 2, and the console count of `h2` elements is 1.

## Exercise 2: Add a sibling CSS section at the correct level.

**Expected evidence:** CSS and HTML both use h2 because they have the same parent topic.

**Approach:** Add a second `section` beside the HTML one inside `main`, with an `h2` titled CSS and its own paragraph.

**Why:** Topics that share a parent share a heading level; an h3 would make CSS a subsection of HTML.

**Plausible wrong approach:** Using `h3` for CSS because it comes second fails because rank describes parentage, not order, so CSS would become a child of HTML.

**How to verify:** `document.querySelectorAll('main > section > h2').length` returns 2 and both headings are siblings in the tree.

## Exercise 3: Build a study page with landmarks and a working skip link.

**Expected evidence:** Header, labeled navigation, one main and footer have meaningful content; the skip target exists.

**Approach:** Place a skip link first in `body`, then `header`, a labeled `nav`, one `main` with a matching `id` and `tabindex="-1"`, and a `footer`.

**Why:** Landmarks let assistive technology jump between regions, and the skip link lets keyboard users bypass repeated navigation; both depend on the target id existing exactly once.

**Plausible wrong approach:** Pointing the skip link at `#main` while the element has `id="content"` fails quietly, because the link renders but moves focus nowhere useful.

**How to verify:** Press Tab once, then Enter; the next Tab press lands on the first focusable element inside `main`, not in the navigation.

## Exercise 4: Replace a heading used only for large text with an appropriate element.

**Expected evidence:** A visual callout uses CSS without corrupting the document outline.

**Approach:** Change the oversized heading to a `p` or `strong` with a class, then reproduce its visual weight with CSS on that class.

**Why:** Headings build the document outline that screen-reader users navigate, so a decorative heading inserts a false section.

**Plausible wrong approach:** Keeping the heading and shrinking it with CSS fails because the outline still lists it as a section title that does not introduce a section.

**How to verify:** The heading count drops by one in the console and the callout still renders with the intended size from the class rule.

## Exercise 5: Check the document with CSS disabled or unavailable.

**Expected evidence:** The reading order and heading relationships remain coherent.

**Approach:** Remove the `style` element or toggle stylesheets off, then read the page top to bottom and through a heading list.

**Why:** Source order is the reading and focus order for most users, so a page that only makes sense visually hides a structural problem.

**Plausible wrong approach:** Checking only the styled page fails because CSS ordering or positioning can make a misordered source look correct on screen.

**How to verify:** Unstyled, the skip link, navigation, the `h1` and each `h2` section appear in the same order as your outline.

## Exercise 6: Explain when a div is more appropriate than section.

**Expected answer:** Use a generic container when grouping does not introduce a meaningful headed section.

**Approach:** Ask whether the group would get a heading in a table of contents; if not, a `div` grouping for layout is the honest element.

**Why:** section represents a thematic group that normally has a heading; div carries no meaning and is right for grouping that exists only for styling.

**Plausible wrong approach:** Wrapping every styled box in `section` fails because each section implies a headed topic, which clutters the outline with nameless regions.

**How to verify:** Each remaining `section` in your page has a heading as its first child, and layout-only wrappers are `div` elements.

## Reference comparison

The reference asserts that the page has exactly one main element and that the first link's hash is #content. That catches a duplicated main and a skip link pointing at the wrong fragment. It cannot judge heading ranks, notice an h3 used for size, or confirm the target actually receives focus, so read the outline and press Tab yourself.

Open `courses/web-development/solutions/web-003_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
