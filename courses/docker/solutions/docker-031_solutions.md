# docker-031: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Continuous integration runs repeatable checks when source changes. A container pipeline can validate source, build an image, test that image and preserve evidence. These are separate stages: passing source tests does not prove the packaged filesystem or startup command is correct.

Artifact promotion means moving an already tested immutable artifact through delivery stages rather than rebuilding slightly different bytes for each stage. Rebuilding with mutable dependencies can break the connection between the tested image and the deployed image. Record the exact source, build inputs and output identity.

Parallel test jobs can reduce elapsed time, but shared fixtures must remain isolated or intentionally serialized. A database test that resets a shared schema cannot be blindly sharded with another writer. The classroom’s grouped suites reflect this principle, while ordinary runtime groups use disposable projects.

A useful pipeline has fast static checks, bounded unit tests, image build, real runtime failure/timeout checks and application acceptance. Store small structured receipts and bounded logs. Always execute cleanup for resources the job owns, including on failures, while preserving evidence needed to diagnose the failure.

For this project, images are built locally in CI for testing and are not pushed to a registry. A portable source ZIP is a different artifact from a built image. Both need their own content and integrity checks.

## Exercise 1: Predict what a unit test cannot prove about packaging.

Unit tests may run in a richer host environment. Execute the final image to observe its real dependency and filesystem contract.

**Expected:** Missing image files or a wrong final command can remain undetected.

## Exercise 2: Separate source ZIP and image artifacts.

They have different consumers and validation requirements. A clean archive does not establish that the image starts.

**Expected:** Source input package versus built executable filesystem.

## Exercise 3: Design a parallel test partition.

Parallelism is valuable only when tests do not corrupt one another’s state. Preserve required serialization for shared resources.

**Expected:** Independent groups with explicit ownership for shared fixtures.

## Exercise 4: Diagnose rebuilding between acceptance and deployment.

Mutable dependencies and timestamps can change output. Promote the tested artifact or qualify the newly built one explicitly.

**Expected:** The new artifact may not match the tested identity.

## Exercise 5: Explain cleanup after a failed CI job.

Failure should not leave a cluster or volume consuming resources indefinitely. Cleanup must not erase the only failure receipt or affect unrelated projects.

**Expected:** Remove job-owned runtime resources while retaining bounded diagnostic evidence.

## Exercise 6: Write a release gate with honest limitations.

A gate should report what ran, not infer broad acceptance from static configuration. Different engines and architectures may still require separate qualification.

**Expected:** Named actual checks on exact artifacts, plus visible skipped surfaces.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
