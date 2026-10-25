# web-060: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

The final project joins HTML structure, CSS presentation, browser interaction, PHP application logic and relational storage around one useful learner journey. Start with a small task: create and review a study plan, receive actionable validation feedback and return later without losing the plan. Expand only after the core behavior is explainable and tested. A framework may help organize a larger application, but it does not remove these contracts.

Use a threat model that names assets, actors, trust boundaries and likely failures. For this learning project, synthetic notes are the data asset; anonymous session ownership is an explicit limitation; request fields are untrusted; output, SQL and filesystem access are separate interpretation boundaries. If adding real accounts, the identity and recovery design must be upgraded deliberately rather than quietly inheriting the anonymous demo's assumptions.

Create an acceptance matrix with normal, invalid, cross-session, restart and accessibility cases. Keep unit checks for pure functions, integration checks for HTTP and storage, and actual browser observations for focus and layout. Connect to the JavaScript and D3 path when adding data visualization, to SQL when expanding relational modeling, and to Docker and Kubernetes when studying delivery. Each extension needs evidence for its new boundary.

## Exercise 1: Define one small learner journey and its finish condition.

The journey ends with an observable saved plan and a clear way to recover from invalid input.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Map every input and output to its validation or encoding boundary.

HTML text, SQL values, URLs, session identity and filesystem paths have distinct policies.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build and review a learner-owned extension of the supplied local lab.

The extension has coherent HTML/CSS, tested PHP behavior and a bounded reproducible setup.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Introduce a controlled invalid request and preserve its evidence.

The application rejects it without a partial write or loss of existing user input.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Perform a stop/resume and a separate restore rehearsal.

The report distinguishes retained volumes from an independently verified recovery copy.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Present a release-readiness review with explicit limits and next actions.

The review connects claims to real evidence and identifies untested platforms or production controls without calling the system bug free.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
