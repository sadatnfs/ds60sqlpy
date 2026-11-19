# web-055: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-055.md`.

## Exercise 1: Explain why pagination needs an explicit stable order.

**Expected answer:** Without it, page boundaries can duplicate or omit records unpredictably.

**Why:** Without an explicit order the database may return rows in any order, so pages can overlap or skip rows.

## Exercise 2: Add a maximum page-size rule.

**Expected evidence:** A caller cannot request an unbounded result.

**Why:** A maximum page size bounds memory, time and response size per request.

## Exercise 3: Implement a cursor-based slice over synthetic records.

**Expected evidence:** The second page continues after the last id and the final page can be shorter.

**Why:** A keyset cursor resumes exactly after the last seen row, and the final page may hold fewer rows than the limit.

## Exercise 4: Diagnose a cache key shared by all authenticated users.

**Expected answer:** The key omits an authorization-dependent dimension and risks data leakage.

**Why:** A cache key must include every authorization dimension, such as the user id, or one user may receive another's data.

## Exercise 5: Test an empty page and an invalid page size.

**Expected evidence:** Empty results are represented normally while invalid budgets are rejected.

**Why:** An empty page is a normal result, while a page size outside the allowed range is an invalid request.

## Exercise 6: Explain what must be measured before claiming a faster database endpoint.

**Expected answer:** Inspect the actual query plan, index, workload, latency distribution and correctness under the target engine.

**Why:** Query plans, index use, workload mix, latency percentiles and correct results on the target engine show whether a change helps.

## Reference comparison

Open `courses/web-development/solutions/web-055_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
