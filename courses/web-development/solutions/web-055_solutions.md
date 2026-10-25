# web-055: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An endpoint should not assume its dataset will remain small. Bound the amount of work and the response size. Pagination returns a portion of a collection under a documented order. Offset pagination is simple but can shift as records are inserted or removed. Cursor pagination identifies a position in a stable ordering and needs a tie-breaker when the primary sort value is not unique.

Caching reuses a previous result, but the cache key and invalidation policy are part of correctness. A key that omits user identity or authorization scope can expose another user's data. A stale result may be acceptable for one display and harmful for another. Define freshness, ownership and failure behavior before using a cache to hide an expensive query.

The reference demonstrates a bounded in-memory cursor over unique increasing ids. It validates the page size, selects ids greater than the cursor and takes only the requested count. This is an algorithm model, not a database query plan or distributed cache. A production query needs a matching index and engine-specific measurement.

## Exercise 1: Explain why pagination needs an explicit stable order.

Without it, page boundaries can duplicate or omit records unpredictably.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a maximum page-size rule.

A caller cannot request an unbounded result.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Implement a cursor-based slice over synthetic records.

The second page continues after the last id and the final page can be shorter.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a cache key shared by all authenticated users.

The key omits an authorization-dependent dimension and risks data leakage.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test an empty page and an invalid page size.

Empty results are represented normally while invalid budgets are rejected.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what must be measured before claiming a faster database endpoint.

Inspect the actual query plan, index, workload, latency distribution and correctness under the target engine.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
