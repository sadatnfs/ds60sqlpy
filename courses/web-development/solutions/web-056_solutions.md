# web-056: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-056.md`.

## Exercise 1: Draw the trust boundary around actor identity and form values.

**Expected answer:** The adapter verifies identity; the application validates proposed domain values.

**Approach:** Mark actor id as trusted because the adapter verified it, and mark every form value as untrusted data that the core must validate.

**Why:** Identity comes from the adapter after verification, while form values are untrusted proposals that the application validates.

**Plausible wrong approach:** Placing actor id inside the form input array fails because the core can no longer tell a verified value from a submitted one.

**How to verify:** The `createPlan` signature takes actor id and input as separate parameters with different names.

## Exercise 2: Write the acceptance matrix before implementing the service.

**Expected evidence:** Normal, invalid and cross-owner cases have explicit observations.

**Approach:** Write rows for valid, invalid and cross owner cases, each with the input, the expected result and the expected row count.

**Why:** An acceptance matrix written first prevents the tests from simply copying what the implementation does.

**Plausible wrong approach:** Writing the matrix after the code passes fails because it then records what the code does instead of what it should do.

**How to verify:** Each matrix row has an observable outcome, and the invalid row expects zero new rows.

## Exercise 3: Build a tested planner core with validation and prepared storage.

**Expected evidence:** Accepted plans persist in the disposable database and rejected inputs create no rows.

**Approach:** Validate into a complete value, insert with a prepared statement, and run the matrix against a fresh memory database.

**Why:** Validating before mutation means a rejected request leaves no partial rows.

**Plausible wrong approach:** Sharing one database across all test cases fails because rows from earlier cases change counts in later ones.

**How to verify:** Every matrix row passes, and the invalid case leaves `SELECT COUNT(*) FROM plans` unchanged.

## Exercise 4: Diagnose a service that writes before validating all fields.

**Expected answer:** Move complete validation before mutation or ensure a correctly owned transaction aborts the entire unit.

**Approach:** Move all validation ahead of the first write, or wrap the writes in a transaction that rolls back on any failure.

**Why:** A write before validation completes can leave partial state unless one transaction rolls it back.

**Plausible wrong approach:** Deleting the partial row in a catch block fails because a crash between insert and delete leaves the orphan anyway.

**How to verify:** Minutes of 500 now raise the rejection and the plans table has the same row count as before.

## Exercise 5: Test cross-owner retrieval and an invalid duration.

**Expected evidence:** No other actor's row is exposed and the invalid request changes no stored state.

**Approach:** Store a plan for actor 1, request it as actor 2, then submit minutes of -1 and count rows before and after.

**Why:** Owner scoping hides other actors' rows, and an invalid request must leave the row count unchanged.

**Plausible wrong approach:** Checking only that actor 2's request did not throw fails because it might have returned actor 1's plan.

**How to verify:** Actor 2 receives null, and the count is the same before and after the invalid request. Actor 1 still receives the plan, confirming the scope blocks only the other actor.

## Exercise 6: Explain the remaining work before this core becomes a deployed application.

**Expected answer:** Real HTTP, session, CSRF, persistence, concurrency, accessibility and operational acceptance remain separate integration tasks.

**Approach:** List each production concern the core leaves out, and name the integration test or review that would cover it.

**Why:** Real HTTP handling, sessions, CSRF, durable storage, concurrency, accessibility and operations each need their own acceptance tests.

**Plausible wrong approach:** Calling the core deployable because the matrix passes fails because no HTTP request, session or real database was involved.

**How to verify:** Your list covers HTTP, sessions, CSRF, persistence, concurrency and accessibility, each with a planned check.

## Reference comparison

Open `courses/web-development/solutions/web-056_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
