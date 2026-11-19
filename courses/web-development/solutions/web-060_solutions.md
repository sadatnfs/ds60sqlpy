# web-060: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-060.md`.

## Exercise 1: Define one small learner journey and its finish condition.

**Expected evidence:** The journey ends with an observable saved plan and a clear way to recover from invalid input.

**Why:** A small journey with a visible finish condition is testable and keeps the scope honest.

## Exercise 2: Map every input and output to its validation or encoding boundary.

**Expected answer:** HTML text, SQL values, URLs, session identity and filesystem paths have distinct policies.

**Why:** HTML text needs escaping, SQL values need parameters, URLs need scheme checks, identity needs the session and paths need ownership.

## Exercise 3: Build and review a learner-owned extension of the supplied local lab.

**Expected evidence:** The extension has coherent HTML/CSS, tested PHP behavior and a bounded reproducible setup.

**Why:** A bounded extension with tests and a reproducible setup can be reviewed by someone else.

## Exercise 4: Introduce a controlled invalid request and preserve its evidence.

**Expected evidence:** The application rejects it without a partial write or loss of existing user input.

**Why:** The preserved evidence shows rejection without partial writes and without losing the user's input.

## Exercise 5: Perform a stop/resume and a separate restore rehearsal.

**Expected evidence:** The report distinguishes retained volumes from an independently verified recovery copy.

**Why:** Resuming proves the volumes were retained, while a restore elsewhere proves the backup itself is usable.

## Exercise 6: Present a release-readiness review with explicit limits and next actions.

**Expected evidence:** The review connects claims to real evidence and identifies untested platforms or production controls without calling the system bug free.

**Why:** A review that links claims to evidence and names untested platforms is credible; calling a system bug free is not.

## Comparing your worksheet

This lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.
