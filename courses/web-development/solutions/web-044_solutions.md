# web-044: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A test compares an observation with an expected contract. A unit test isolates a small behavior; an integration test exercises a boundary such as a database or HTTP server. Both are useful, and neither should be mislabeled as the other. A reference program that prints a success marker without checking the relevant behavior provides weak evidence.

Good cases include ordinary input, an empty or zero boundary, invalid types or ranges, and a previously observed failure. Tests should explain why the expected result is correct instead of repeating the implementation's internal steps. A function and its test can share the same bug if the expected value is computed using the same faulty algorithm.

This course uses a tiny check function that throws RuntimeException on failure, making behavior independent of whether PHP assertions are enabled. Test exceptions by recording whether the expected exception occurred, then check that flag. Do not catch every exception and treat it as the expected one. Full projects can adopt a prepared testing framework, but no dependency installation is needed here.

## Exercise 1: Classify a pure-function check and a real database transaction check.

The first is unit evidence; the second is integration evidence.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add an empty-input test with an explicit expected result.

The test records the domain policy rather than guessing from the implementation.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Create a test table for a bounded study-duration function.

Normal, zero, invalid and boundary cases have independently justified outcomes.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a test that catches the wrong exception as success.

Catch the declared exception narrowly and let unexpected failures remain failures.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Temporarily introduce a known bug in a learner copy.

A meaningful test fails for the intended reason, then passes after the repair.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why a passing reference is not a bug-free guarantee.

It qualifies the tested contract and cases; untested integration and environment behavior remain separate.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
