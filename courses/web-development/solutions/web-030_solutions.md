# web-030: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-030.md`.

## Exercise 1: Map a label, interaction and layout claim to different evidence.

**Expected answer:** Use structural checks, actual interaction and visual inspection respectively.

**Why:** Structure can be checked in the DOM, behavior needs a real interaction and appearance needs visual inspection.

## Exercise 2: Turn one silent assumption into a throwing assertion.

**Expected evidence:** A violated invariant produces a clear failure message.

**Why:** An explicit assertion turns a silent wrong state into a visible failure with a useful message.

## Exercise 3: Create a quality report for the portal from web-024.

**Expected evidence:** The report records source revision, tested conditions, observations and remaining limitations.

**Why:** A dated, scoped report lets someone else repeat the review and see its limits.

## Exercise 4: Diagnose a test that passes before an interaction later throws.

**Expected answer:** Inspect the settled state and errors after all representative actions.

**Why:** A check that runs before the interaction misses errors that only happen after it.

## Exercise 5: Repeat the review after narrow resizing and a saved-page reload.

**Expected evidence:** The interface remains usable and the learner distinguishes persisted source from transient preview state.

**Why:** Reloading separates what was saved, the source, from transient preview state.

## Exercise 6: Explain what evidence would justify a production readiness claim.

**Expected answer:** It requires broader integration, security, accessibility, operational and workload-specific performance evidence than one local reference run.

**Why:** Production readiness needs integration, security, accessibility, operational and real-workload performance evidence that a single preview cannot supply.

## Reference comparison

Open `courses/web-development/solutions/web-030_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
