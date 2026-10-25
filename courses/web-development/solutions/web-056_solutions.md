# web-056: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

The application core coordinates a use case without pretending to be an HTTP server. It receives a trusted actor identity and untrusted proposed values, validates the proposal, writes through a repository and returns a result. Keeping these boundaries visible makes it possible to reason about what is trusted and which failures prevent a write.

This milestone combines the earlier mechanisms in a small study planner. The database is disposable SQLite memory. The input is synthetic. Validation rejects unsupported topics and out-of-range durations. A prepared statement stores an accepted plan under the supplied actor. A query scopes retrieval by that actor. Rendering and HTTP adaptation remain separate so the same core can later be integrated and tested through a real server.

Write the acceptance matrix before implementation: a valid plan is stored once, invalid input stores nothing, one actor cannot read another's plan, and output has a clear type contract. A production service would add session verification, CSRF where relevant, idempotency, concurrent behavior, migrations and operational controls. Do not infer those properties from this small core.

## Exercise 1: Draw the trust boundary around actor identity and form values.

The adapter verifies identity; the application validates proposed domain values.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Write the acceptance matrix before implementing the service.

Normal, invalid and cross-owner cases have explicit observations.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a tested planner core with validation and prepared storage.

Accepted plans persist in the disposable database and rejected inputs create no rows.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a service that writes before validating all fields.

Move complete validation before mutation or ensure a correctly owned transaction aborts the entire unit.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test cross-owner retrieval and an invalid duration.

No other actor's row is exposed and the invalid request changes no stored state.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the remaining work before this core becomes a deployed application.

Real HTTP, session, CSRF, persistence, concurrency, accessibility and operational acceptance remain separate integration tasks.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
