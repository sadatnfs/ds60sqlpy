# docker-028: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A registry stores image manifests and blobs for distribution. A repository groups related image names inside that registry. Authentication determines who can access the registry; authorization determines which operations that identity may perform. Public pull access is different from permission to overwrite a release tag.

A local tag does not publish anything. Publication is a deliberate operation with credentials, destination, retention and rollback implications. This course uses local builds and offline exports by default. You can study a registry workflow without pushing the course or your private code anywhere.

Mutable tags such as latest are useful conveniences but weak deployment identities. A release procedure should resolve or record an immutable digest and relate it to source, build inputs and acceptance evidence. A registry availability problem should not cause an operator to deploy a different unreviewed image merely because its tag looks similar.

Read a reference as registry/repository:tag or registry/repository@digest. A tag may point to a platform index, which then selects a platform manifest. Keep that level of identity clear when comparing builds. Registry credentials belong in an approved credential store or short-lived CI mechanism, never in a Dockerfile.

The examples below inspect local metadata and a conceptual release record. They intentionally contain no push command. If you later publish your own project, make the destination and intended visibility explicit and verify the uploaded immutable identity after publication.

## Exercise 1: Parse the components of an image reference.

The registry location and image identity should be unambiguous before any authenticated operation. A familiar short tag can hide a different destination.

**Expected:** Registry, repository, optional tag and optional digest.

## Exercise 2: Predict whether adding a local tag uploads bytes.

This separation lets you prepare and inspect an artifact without distributing it. Publication requires its own intentional command and authorization.

**Expected:** No; local naming and registry publication are separate.

## Exercise 3: Design a release identity record.

The record should join source and runtime evidence. A tag alone cannot preserve that relationship if it is later moved.

**Expected:** Source revision, immutable image identity, platform and tested behavior.

## Exercise 4: Diagnose an overwritten mutable release tag.

The same label can name different content. Resolve the exact identity before concluding that earlier acceptance evidence applies.

**Expected:** Compare recorded digest with the currently resolved artifact.

## Exercise 5: Explain why credentials do not belong in the build context.

Registry access is an operation credential, not application source. Use a reviewed credential channel and avoid printing values during diagnostics.

**Expected:** They can be transferred, layered or logged beyond the intended lifetime.

## Exercise 6: Describe a safe publication review without performing it.

A reviewable proposal is concrete enough to approve. It should not upload a different artifact later or silently change repository visibility.

**Expected:** Explicit destination, visibility, immutable artifact and rollback plan.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
