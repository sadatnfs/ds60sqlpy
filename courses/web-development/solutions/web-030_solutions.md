# web-030: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Quality is a set of observable contracts. A structural test can check that a button has a label. An interaction test can check that it changes the intended value. A visual inspection can reveal clipping after resizing. An assistive-technology review can expose an announcement problem. No single kind of test proves all of these. Plan the evidence around the behavior you claim.

Performance also requires a defined workload and measurement boundary. Loading, parsing, scripting, layout, painting and network transfer contribute differently. A tiny function timer is not page-load performance. Warm caches, device speed, background activity and instrumentation affect measurements. Report the conditions and distributions instead of declaring an arbitrary universal millisecond target.

Use explicit assertions that throw on failure rather than relying only on console.assert. Keep a deterministic fixture for logic tests and a separate manual checklist for keyboard, zoom, narrow width, print and reduced motion. Measure a bounded task with performance.now only when explaining that local task. Do not interpret a microbenchmark as a production capacity claim.

## Exercise 1: Map a label, interaction and layout claim to different evidence.

Use structural checks, actual interaction and visual inspection respectively.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Turn one silent assumption into a throwing assertion.

A violated invariant produces a clear failure message.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Create a quality report for the portal from web-024.

The report records source revision, tested conditions, observations and remaining limitations.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a test that passes before an interaction later throws.

Inspect the settled state and errors after all representative actions.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Repeat the review after narrow resizing and a saved-page reload.

The interface remains usable and the learner distinguishes persisted source from transient preview state.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what evidence would justify a production readiness claim.

It requires broader integration, security, accessibility, operational and workload-specific performance evidence than one local reference run.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
