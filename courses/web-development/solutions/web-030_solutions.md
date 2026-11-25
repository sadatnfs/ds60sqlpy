# web-030: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-030.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Map a label, interaction and layout claim to different evidence.

**Expected answer:** Use structural checks, actual interaction and visual inspection respectively.

**Approach:** Assign each claim a matching method: query the DOM for labels, press keys for interaction, and look at the rendered page for layout.

**Why:** Structure can be checked in the DOM, behavior needs a real interaction and appearance needs visual inspection.

**Plausible wrong approach:** Using a DOM query to prove that a layout fits fails because the structure can be correct while elements overflow visually.

**How to verify:** Your table pairs the label, interaction and layout claims with three different methods, and each row has its own recorded result and date.

## Exercise 2: Turn one silent assumption into a throwing assertion.

**Expected evidence:** A violated invariant produces a clear failure message.

**Approach:** Write `if (!condition) throw new Error('...')` with a message that names the expected and the actual value.

**Why:** An explicit assertion turns a silent wrong state into a visible failure with a useful message.

**Plausible wrong approach:** Using `console.assert` fails because it only logs the problem and lets the run end looking successful.

**How to verify:** Breaking the condition makes the script stop with your message instead of reaching the final log line.

## Exercise 3: Create a quality report for the portal from web-024.

**Expected evidence:** The report records source revision, tested conditions, observations and remaining limitations.

**Approach:** Record the source revision or file date, the browser and window size, and a line for each check with what happened.

**Why:** A dated, scoped report lets someone else repeat the review and see its limits.

**Plausible wrong approach:** Writing a report that says only all good fails because no reader can tell which conditions were checked or when.

**How to verify:** Another person can repeat each check from your report alone and compare their results line by line.

## Exercise 4: Diagnose a test that passes before an interaction later throws.

**Expected answer:** Inspect the settled state and errors after all representative actions.

**Approach:** Run every representative interaction first, then read the console and DOM in the settled state before declaring a result.

**Why:** A check that runs before the interaction misses errors that only happen after it.

**Plausible wrong approach:** Asserting only on initial load fails because an error thrown after the first click never reaches the test.

**How to verify:** After the full interaction sequence, the console shows no uncaught errors and the final state matches expectations.

## Exercise 5: Repeat the review after narrow resizing and a saved-page reload.

**Expected evidence:** The interface remains usable and the learner distinguishes persisted source from transient preview state.

**Approach:** Resize to the narrow preset, interact, save the source, reload, and compare which values persist and which reset.

**Why:** Reloading separates what was saved, the source, from transient preview state.

**Plausible wrong approach:** Assuming a counter value survives reload fails because in-memory state is cleared and only saved source remains.

**How to verify:** After reload the counter shows its starting value again, while your edited source changes are still present and the narrow layout still has no sideways scrolling.

## Exercise 6: Explain what evidence would justify a production readiness claim.

**Expected answer:** It requires broader integration, security, accessibility, operational and workload-specific performance evidence than one local reference run.

**Approach:** List evidence types a production claim needs: integration tests, security review, accessibility audit, operations plan and load measurements.

**Why:** Production readiness needs integration, security, accessibility, operational and real-workload performance evidence that a single preview cannot supply.

**Plausible wrong approach:** Citing a fast `performance.now` timing fails because one tiny sort says nothing about real traffic, devices or data sizes.

**How to verify:** Your answer names at least four evidence types, none of which this local reference run provides.

## Reference comparison

The reference requires one main element and a non-empty button label, clicks the button, then requires the output to mention Manual. That catches missing structure and a status that claims more than it checked. It does not test keyboard use, resizing, zoom or performance, so record those observations separately as the checklist asks.

Open `courses/web-development/solutions/web-030_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
