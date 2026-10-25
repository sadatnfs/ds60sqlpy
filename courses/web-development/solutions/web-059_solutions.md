# web-059: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A production PHP deployment commonly separates an HTTP server or reverse proxy from a PHP process manager. PHP-FPM manages FastCGI workers; it is not itself a general browser-facing HTTP server. A web server routes appropriate requests to the runtime and serves approved static assets. The public document root should contain only files intended for delivery, keeping source configuration, dependency metadata, private data and secrets outside that boundary.

A container packages a runtime and application, while volumes or external storage hold durable state. Rebuilding an image does not migrate a database automatically. A release needs a plan for schema changes, compatibility, rollback, backup and restore. A backup job reporting success is weaker evidence than an actual restore that recreates the expected data and application behavior.

Use reviewed locked dependencies and a deliberate image tag or digest policy. Supply secrets through a controlled runtime mechanism rather than baking them into images or committing them. Enable appropriate error logging without displaying internal stack traces publicly. TLS termination and trusted proxy headers require an explicit network ownership policy; do not trust forwarded identity or scheme headers from arbitrary clients.

## Exercise 1: Explain why PHP-FPM is not interchangeable with the development HTTP server.

FPM manages FastCGI workers and needs an appropriate HTTP-facing integration.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Draw the public document root and private application directories.

Only intended static assets and entrypoints are directly served.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Design a release plan for the study planner with durable storage.

The plan covers configuration, secrets, migration, health, write/read acceptance, backup and rollback.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose secrets copied into an image layer.

Removing them in a later layer does not reliably erase earlier layer content; rotate exposed secrets and rebuild correctly.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Describe a restore test in a separate disposable environment.

Recovered data and application behavior must be checked without overwriting the active store.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what evidence is needed before publishing an image as ready.

Source, dependency, runtime, browser, data recovery and target-environment checks need explicit results and limits.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
