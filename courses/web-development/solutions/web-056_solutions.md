# web-056: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-056.md`.

## Exercise 1: Draw the trust boundary around actor identity and form values.

**Expected answer:** The adapter verifies identity; the application validates proposed domain values.

**Why:** Identity comes from the adapter after verification, while form values are untrusted proposals that the application validates.

## Exercise 2: Write the acceptance matrix before implementing the service.

**Expected evidence:** Normal, invalid and cross-owner cases have explicit observations.

**Why:** An acceptance matrix written first prevents the tests from simply copying what the implementation does.

## Exercise 3: Build a tested planner core with validation and prepared storage.

**Expected evidence:** Accepted plans persist in the disposable database and rejected inputs create no rows.

**Why:** Validating before mutation means a rejected request leaves no partial rows.

## Exercise 4: Diagnose a service that writes before validating all fields.

**Expected answer:** Move complete validation before mutation or ensure a correctly owned transaction aborts the entire unit.

**Why:** A write before validation completes can leave partial state unless one transaction rolls it back.

## Exercise 5: Test cross-owner retrieval and an invalid duration.

**Expected evidence:** No other actor's row is exposed and the invalid request changes no stored state.

**Why:** Owner scoping hides other actors' rows, and an invalid request must leave the row count unchanged.

## Exercise 6: Explain the remaining work before this core becomes a deployed application.

**Expected answer:** Real HTTP, session, CSRF, persistence, concurrency, accessibility and operational acceptance remain separate integration tasks.

**Why:** Real HTTP handling, sessions, CSRF, durable storage, concurrency, accessibility and operations each need their own acceptance tests.

## Reference comparison

Open `courses/web-development/solutions/web-056_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
