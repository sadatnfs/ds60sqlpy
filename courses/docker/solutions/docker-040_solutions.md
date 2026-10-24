# docker-040: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A runtime secret is sensitive input required while an application runs. It has a different lifecycle from a build secret. Compose can expose declared secrets as files to selected services, while ordinary configuration can be passed through environment variables or files. The exact storage and protection depend on the deployment platform.

Local Compose file-based secrets are not a universal encrypted secret vault. The source file exists on the host and must be protected there. File mounts can avoid some environment-variable exposure paths, but the application can still read and accidentally log the value. Secret handling is a complete data-flow concern.

This lesson uses only an invented value. Never copy a real credential into the repository, a screenshot or a public report. The course fixture needs no password, so the optional example belongs in a separate scratch project and demonstrates a file-reading contract rather than adding a secret requirement to the app.

A top-level `secrets` entry declares a source, and a service grants itself access by name. Inside the service the file commonly appears under `/run/secrets/NAME`. The app must explicitly read that file or support a documented file-based configuration option.

Rotate a credential by updating the controlled source and applying the appropriate service lifecycle, then verify the new identity and revoke the old credential according to the external service policy. A container restart alone does not prove that an old credential has been invalidated.

## Exercise 1: Compare build and runtime secrets.

Their consumers and lifetimes differ. A build-only credential should not be copied into the final runtime image.

**Expected:** Temporary build input versus application-time input.

## Exercise 2: Predict whether a local secret file is automatically encrypted everywhere.

The secret abstraction controls delivery, not every storage layer. Describe the actual local Compose implementation honestly.

**Expected:** No; host storage and platform behavior require separate protection.

## Exercise 3: Design a no-disclosure validation message.

Useful diagnostics need not reveal bytes. Avoid including environment dumps, full headers or file contents in error reports.

**Expected:** Report presence or a bounded error without the sensitive value.

## Exercise 4: Diagnose a secret declared but not granted to a service.

Check the effective model and service access list before changing file permissions or adding a broad host mount.

**Expected:** The service lacks the intended mounted input.

## Exercise 5: Explain credential rotation beyond restarting a container.

The external service decides which credential remains valid. A process lifecycle event alone cannot establish that policy change.

**Expected:** New input must be applied and old authority revoked deliberately.

## Exercise 6: Write a secret data-flow review.

Following the bytes through their lifetime reveals exposure paths that a single Compose setting cannot address.

**Expected:** Source, host protection, service grant, read path, logs, rotation and deletion.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
