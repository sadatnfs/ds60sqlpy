# web-024: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-024.md`.

## Exercise 1: Write three learner tasks before drawing the interface.

**Expected evidence:** Find a topic, assess its prerequisites and choose a clear next action.

**Approach:** Write each task as a learner goal with a verb and an object, such as find a topic, check its prerequisites and choose a next step.

**Why:** Starting from tasks keeps the interface focused on finding a topic, checking prerequisites and taking the next step.

**Plausible wrong approach:** Starting with a color palette or a hero image fails because the layout then serves decoration, and no criterion tells you when the page is done.

**How to verify:** Each card in the finished page answers one written task, and you can point to the element that does it.

## Exercise 2: Define a small token set for the page.

**Expected evidence:** Spacing, text and surface choices are consistent and named by role.

**Approach:** Define tokens such as `--space`, `--text` and `--surface` in `:root`, named for the role they play, and use them in every card rule.

**Why:** A small role-based token set keeps the page consistent and makes later palette changes safe.

**Plausible wrong approach:** Naming tokens after hues such as `--blue` fails because a later palette change leaves names that no longer describe the value.

**How to verify:** Changing `--space` once updates every card gap and padding, and the tokens appear in the Computed panel.

## Exercise 3: Build a complete offline portal with three paths and local destinations.

**Expected evidence:** All cards, navigation and headings are meaningful, keyboard reachable and responsive.

**Approach:** Build one `main`, a navigation list, three `article` cards with headings, prerequisites and specific links, and the auto-fit grid from worked example 2.

**Why:** A meaningful structure keeps the portal usable without styles, and the CSS then adapts it to different widths.

**Plausible wrong approach:** Adding a progress bar that claims saved progress fails because static HTML has no storage, so the number is invented.

**How to verify:** Every link reaches a matching local `id`, Tab visits each card link in reading order, and the grid stacks at narrow width.

## Exercise 4: Audit one deliberately vague link and one broken fragment.

**Expected evidence:** Replace the vague label and repair the target relationship.

**Approach:** List all link names out of context, then click each fragment link and confirm the target `id` exists exactly once.

**Why:** Link text must describe its destination, and every fragment must match an existing id.

**Plausible wrong approach:** Fixing the vague label with `title` text fails because many readers never see tooltips and the accessible name may stay Read more.

**How to verify:** The links list shows distinct names, and every fragment scrolls to its matching heading.

## Exercise 5: Review narrow width, zoom, keyboard and print behavior.

**Expected evidence:** Retain observations for each surface instead of claiming a universal pass from one screenshot.

**Approach:** Record separate notes for narrow width, 200 percent zoom, keyboard only and print preview, each with what you saw and the browser used.

**Why:** Narrow width, zoom, keyboard and print each exercise different behavior, so each needs its own evidence.

**Plausible wrong approach:** Writing a single pass line for the whole portal fails because a later reader cannot tell which surface was actually checked.

**How to verify:** Your notes contain four dated entries, each naming the condition, the observation and any remaining problem.

## Exercise 6: Explain the portal's remaining backend requirements.

**Expected answer:** Persistent identity, saved progress and authorization need a server and storage contract beyond this static page.

**Approach:** Separate what the static page does from features that need storage, identity or permissions, and name the server piece each one requires.

**Why:** Saved progress, identity and permissions require a server and storage; a static page can only describe them.

**Plausible wrong approach:** Using `localStorage` and calling it saved progress fails because it is tied to one browser and gives no account or authorization.

**How to verify:** Your explanation names at least sign-in, a progress table and an authorization check, none implemented in the static page.

## Reference comparison

Open `courses/web-development/solutions/web-024_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
