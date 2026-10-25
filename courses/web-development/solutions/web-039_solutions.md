# web-039: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An exception interrupts the ordinary flow and can be handled by a matching catch block. It is useful when a function cannot fulfill its contract. A catch block should either recover meaningfully, translate the error into an appropriate boundary response or rethrow it. Catching every failure and returning a normal-looking value can corrupt downstream reasoning.

PHP has different error categories, and not every warning automatically becomes an exception. Runtime configuration and library behavior matter. A production error boundary should avoid exposing stack traces, secrets or internal paths to visitors while retaining an appropriate diagnostic record for maintainers. The local classroom output is a teaching surface, not a production logging policy.

Catch specific exceptions near an operation when a specific recovery exists. Use finally for cleanup that should happen whether the operation succeeds or fails. Keep validation errors distinct from unexpected internal failures. An invalid user field can produce a clear correction; an unavailable database may require a generic retry message and internal diagnosis.

## Exercise 1: Trace the statements executed after requirePositive(0).

The function throws, the matching catch runs and finally executes.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a specific catch around a recoverable validation error.

The caller presents a correction without hiding unrelated failures.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a failure-aware parser with explicit success and error paths.

Valid data returns a result; invalid data produces a clear classified failure.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a catch-all that returns zero for every failure.

A fabricated normal value hides the difference between valid zero and broken processing.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test cleanup after both success and exception.

Owned resources are released in either path.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the difference between learner diagnostics and public production errors.

Detailed local diagnostics support learning, while public responses should avoid sensitive internal detail.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
