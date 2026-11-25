# web-004: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-004.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Resolve ../images/plot.svg from /notes/week1/page.html.

**Expected answer:** The resolved path is /notes/images/plot.svg on the same origin.

**Approach:** Drop the file name `page.html` to get the base `/notes/week1/`, apply `..` once to reach `/notes/`, then append `images/plot.svg`.

**Why:** The base directory is /notes/week1/; .. moves up to /notes/, then images/plot.svg is appended, and the scheme and host stay the same.

**Plausible wrong approach:** Resolving from `/notes/week1/page.html/` as if the file were a directory fails because it leaves you one level too deep, at `/notes/week1/images/`.

**How to verify:** Run `new URL('../images/plot.svg', 'https://example.test/notes/week1/page.html').pathname` in the console and read /notes/images/plot.svg.

## Exercise 2: Replace vague link text with destination-specific wording.

**Expected evidence:** The link makes sense outside its surrounding sentence.

**Approach:** Rewrite each link so the text alone names the destination, such as Read the methods section instead of Click here.

**Why:** People often navigate by a list of links, where text such as click here gives no destination.

**Plausible wrong approach:** Adding a long `title` attribute to a vague link fails because many users never see the tooltip and link lists still read Click here.

**How to verify:** Read only the link texts in order, out of context; each one still tells you where it goes.

## Exercise 3: Build a contents list that navigates to three local sections.

**Expected evidence:** Every fragment matches one unique section id and works with keyboard activation.

**Approach:** Write three sections with unique ids first, then build the contents list by copying each id exactly into an `href` that begins with `#`.

**Why:** A fragment link scrolls to the element whose id matches; a duplicate or missing id makes the target ambiguous or absent.

**Plausible wrong approach:** Typing the ids twice by hand fails easily, since a single letter or case difference produces a link with no target.

**How to verify:** Tab to each contents link and press Enter; the URL fragment changes and the matching heading scrolls into view each time.

## Exercise 4: Diagnose a link whose fragment has no matching id.

**Expected answer:** The link has no intended target even if its visual style looks correct.

**Approach:** Read the link's `href`, strip the `#`, and search the document for an element with exactly that `id`.

**Why:** Fragment matching is exact and case-sensitive, so a link can look correct and still have no target.

**Plausible wrong approach:** Judging by the link's styling fails because a broken fragment link looks identical to a working one until it is activated.

**How to verify:** `document.getElementById('method')` returns null for the broken target, and returns the section after the `id` and `href` match.

## Exercise 5: Distinguish a disabled action from an unavailable destination.

**Expected answer:** A button can be disabled; a meaningful alternative explanation should replace a dead link.

**Approach:** Use a `button` with the `disabled` attribute for an action that is temporarily unavailable, and plain explanatory text where a destination does not exist.

**Why:** Buttons have a disabled state that blocks activation, while links do not; an unavailable destination should be explained in text instead of left as a dead link.

**Plausible wrong approach:** Leaving `<a href="#">` for a missing page fails because it still looks clickable, jumps to the top and gives no reason.

**How to verify:** The disabled button is skipped by Tab, and the unavailable destination is described in text with no focusable dead link.

## Exercise 6: Explain the difference between absolute, root-relative and document-relative paths.

**Expected answer:** Each has a distinct base and can resolve differently when the document moves.

**Approach:** Resolve the same target with three hrefs: a full `https://` URL, a path starting with `/`, and a `../` path, noting the base each uses.

**Why:** An absolute URL includes scheme and host, a root-relative path starts at the site root and a document-relative path depends on the current document's directory, so only the last one changes when the page moves.

**Plausible wrong approach:** Treating root-relative and document-relative paths as interchangeable fails as soon as the page moves to another folder.

**How to verify:** Changing the base URL in a `new URL(href, base)` console call alters the relative result but not the absolute one.

## Reference comparison

The reference loops over the navigation links and requires that each hash finds an element in the document, so it catches a fragment like #result that does not match the section id. It does not judge link wording, test relative file paths or check that the destination section has a heading, so review the link text yourself.

Open `courses/web-development/solutions/web-004_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
