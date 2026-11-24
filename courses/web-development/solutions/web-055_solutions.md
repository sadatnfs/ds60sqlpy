# web-055: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-055.md`.

## Exercise 1: Explain why pagination needs an explicit stable order.

**Expected answer:** Without it, page boundaries can duplicate or omit records unpredictably.

**Approach:** Note that a database may return rows in any order without ORDER BY, so page boundaries are only defined for a fixed sort.

**Why:** Without an explicit order the database may return rows in any order, so pages can overlap or skip rows.

**Plausible wrong approach:** Relying on insertion order because it looks stable in a small test fails because the engine may change order after updates or plan changes.

**How to verify:** Your explanation shows ORDER BY on a unique key such as id in every page query.

## Exercise 2: Add a maximum page-size rule.

**Expected evidence:** A caller cannot request an unbounded result.

**Approach:** Reject page sizes below 1 or above a maximum such as 50 before any records are sliced.

**Why:** A maximum page size bounds memory, time and response size per request.

**Plausible wrong approach:** Silently clamping 100000 down to 50 without telling the caller fails because the client may assume it received everything.

**How to verify:** A size of 0 and a size of 1000 both return a validation error, while 50 succeeds.

## Exercise 3: Implement a cursor-based slice over synthetic records.

**Expected evidence:** The second page continues after the last id and the final page can be shorter.

**Approach:** Filter records with id greater than the cursor, keep the first size items, and return the last id as the next cursor.

**Why:** A keyset cursor resumes exactly after the last seen row, and the final page may hold fewer rows than the limit.

**Plausible wrong approach:** Using the page number times size as the next starting position fails because it is offset paging with a different name.

**How to verify:** With ids 1 through 5 and size 2, the pages are [1, 2], [3, 4] and [5], then an empty page.

## Exercise 4: Diagnose a cache key shared by all authenticated users.

**Expected answer:** The key omits an authorization-dependent dimension and risks data leakage.

**Approach:** Add the actor id and any permission dimension to the cache key so each user's data gets its own entry.

**Why:** A cache key must include every authorization dimension, such as the user id, or one user may receive another's data.

**Plausible wrong approach:** Shortening the cache lifetime to one second fails because another user can still receive the cached data within that second.

**How to verify:** Two actors requesting the same page produce two different keys and two separate entries.

## Exercise 5: Test an empty page and an invalid page size.

**Expected evidence:** Empty results are represented normally while invalid budgets are rejected.

**Approach:** Request a page after the last id and a page with size -1, and compare the two responses.

**Why:** An empty page is a normal result, while a page size outside the allowed range is an invalid request.

**Plausible wrong approach:** Returning an error for an empty page fails because reaching the end of the list is a normal outcome, not a client mistake.

**How to verify:** The empty page returns an empty items list with status success, while size -1 returns a validation error.

## Exercise 6: Explain what must be measured before claiming a faster database endpoint.

**Expected answer:** Inspect the actual query plan, index, workload, latency distribution and correctness under the target engine.

**Approach:** Run EXPLAIN on the target engine, check that the cursor uses an index, and measure latency percentiles under a realistic workload.

**Why:** Query plans, index use, workload mix, latency percentiles and correct results on the target engine show whether a change helps.

**Plausible wrong approach:** Timing the in memory slice and calling the database endpoint fast fails because no query plan or index was involved.

**How to verify:** Your plan names the index, the EXPLAIN output to check and a latency percentile to record.

## Reference comparison

Open `courses/web-development/solutions/web-055_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
