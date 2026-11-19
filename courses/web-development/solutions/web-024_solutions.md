# web-024: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-024.md`.

## Exercise 1: Write three learner tasks before drawing the interface.

**Expected evidence:** Find a topic, assess its prerequisites and choose a clear next action.

**Why:** Starting from tasks keeps the interface focused on finding a topic, checking prerequisites and taking the next step.

## Exercise 2: Define a small token set for the page.

**Expected evidence:** Spacing, text and surface choices are consistent and named by role.

**Why:** A small role-based token set keeps the page consistent and makes later palette changes safe.

## Exercise 3: Build a complete offline portal with three paths and local destinations.

**Expected evidence:** All cards, navigation and headings are meaningful, keyboard reachable and responsive.

**Why:** A meaningful structure keeps the portal usable without styles, and the CSS then adapts it to different widths.

## Exercise 4: Audit one deliberately vague link and one broken fragment.

**Expected evidence:** Replace the vague label and repair the target relationship.

**Why:** Link text must describe its destination, and every fragment must match an existing id.

## Exercise 5: Review narrow width, zoom, keyboard and print behavior.

**Expected evidence:** Retain observations for each surface instead of claiming a universal pass from one screenshot.

**Why:** Narrow width, zoom, keyboard and print each exercise different behavior, so each needs its own evidence.

## Exercise 6: Explain the portal's remaining backend requirements.

**Expected answer:** Persistent identity, saved progress and authorization need a server and storage contract beyond this static page.

**Why:** Saved progress, identity and permissions require a server and storage; a static page can only describe them.

## Reference comparison

Open `courses/web-development/solutions/web-024_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
