# web-060: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-060.md`.

## Exercise 1: Define one small learner journey and its finish condition.

**Expected evidence:** The journey ends with an observable saved plan and a clear way to recover from invalid input.

**Approach:** Choose one journey, such as entering a plan with the keyboard, and state the observable end: the saved plan appears after the redirect.

**Why:** A small journey with a visible finish condition is testable and keeps the scope honest.

**Plausible wrong approach:** Defining the journey as the user is happy fails because nobody can observe or test that condition.

**How to verify:** Your finish condition names a specific screen state that another person could check. The condition also names the recovery path shown after an invalid entry.

## Exercise 2: Map every input and output to its validation or encoding boundary.

**Expected answer:** HTML text, SQL values, URLs, session identity and filesystem paths have distinct policies.

**Approach:** Make a table with each input and output, its destination context and its rule, such as HTML escaping or a bound SQL value.

**Why:** HTML text needs escaping, SQL values need parameters, URLs need scheme checks, identity needs the session and paths need ownership.

**Plausible wrong approach:** Applying one sanitize function to every field fails because HTML, SQL, URLs and paths each need different rules.

**How to verify:** Every row in your table names a specific function or check, and no two contexts share a generic rule.

## Exercise 3: Build and review a learner-owned extension of the supplied local lab.

**Expected evidence:** The extension has coherent HTML/CSS, tested PHP behavior and a bounded reproducible setup.

**Approach:** Copy the lab into your own directory, add one small feature with a test, and record the commands that rebuild it.

**Why:** A bounded extension with tests and a reproducible setup can be reviewed by someone else.

**Plausible wrong approach:** Editing the shared fixture in place fails because updates to the course then overwrite your work or conflict with it.

**How to verify:** A fresh clone plus your recorded commands rebuilds the extension and its tests pass.

## Exercise 4: Introduce a controlled invalid request and preserve its evidence.

**Expected evidence:** The application rejects it without a partial write or loss of existing user input.

**Approach:** Send one request with a known bad value, save the status and body, and count rows before and after.

**Why:** The preserved evidence shows rejection without partial writes and without losing the user's input.

**Plausible wrong approach:** Describing the rejection from memory fails because the report then has no evidence a reviewer can compare against.

**How to verify:** Your saved evidence shows the rejection response and an unchanged row count.

## Exercise 5: Perform a stop/resume and a separate restore rehearsal.

**Expected evidence:** The report distinguishes retained volumes from an independently verified recovery copy.

**Approach:** Stop and start the lab to check retained volumes, then separately restore a backup into a fresh environment and compare data.

**Why:** Resuming proves the volumes were retained, while a restore elsewhere proves the backup itself is usable.

**Plausible wrong approach:** Calling the stop and start a backup test fails because the same volumes were reused, so no copy was ever restored.

**How to verify:** Your report shows two separate results, one for restart and one for the restored copy.

## Exercise 6: Present a release-readiness review with explicit limits and next actions.

**Expected evidence:** The review connects claims to real evidence and identifies untested platforms or production controls without calling the system bug free.

**Approach:** List each claim with its evidence, then list what remains untested, and propose the next action for each gap.

**Why:** A review that links claims to evidence and names untested platforms is credible; calling a system bug free is not.

**Plausible wrong approach:** Writing ready for production without listing limits fails because readers then assume TLS, accounts and scaling were checked.

**How to verify:** Every claim in your review links to an observation, and the gaps list has at least three items.

## Comparing your worksheet

This lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.
