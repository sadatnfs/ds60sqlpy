# docker-040: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-040.md).

## Exercise 1: Compare build and runtime secrets.

**Expected answer:** Temporary build input versus application-time input.

**Why:** Their consumers and lifetimes differ. A build-only credential should not be copied into the final runtime image.

**Approach:** Separate when each secret is needed: a build secret serves one RUN step; a runtime secret like demo is read while the app runs.

**Why this is correct:** A build-only credential that ends up in the runtime image stays readable for the image's whole life.

**A plausible wrong approach:** Using the same token for build and runtime and copying it into the image to reuse it widens exposure.

**How to verify:** The final image lacks the build credential, and the app reads demo from /run/secrets at runtime only.

## Exercise 2: Predict whether a local secret file is automatically encrypted everywhere.

**Expected answer:** No; host storage and platform behavior require separate protection.

**Why:** The secret abstraction controls delivery, not every storage layer. Describe the actual local Compose implementation honestly.

**Approach:** Ask where demo-secret.txt lives: in plain form on the host, protected only by host file permissions.

**Why this is correct:** Local Compose delivers the file into the container; it does not encrypt the host copy.

**A plausible wrong approach:** Treating the secrets key as encryption leaves the host file readable by other local users if its mode allows.

**How to verify:** ls -l on the host file shows its mode and owner, which set who can read it.

## Exercise 3: Design a no-disclosure validation message.

**Expected evidence:** Report presence or a bounded error without the sensitive value.

**Why:** Useful diagnostics need not reveal bytes. Avoid including environment dumps, full headers or file contents in error reports.

**Approach:** Read the worked example's check: it reads the file, rejects empty content, and prints only that input is present.

**Why this is correct:** The message proves the secret is configured without writing its bytes to output or logs.

**A plausible wrong approach:** Printing the value to confirm it loaded copies it into logs that others may read.

**How to verify:** Run the check with an empty file and a filled file; the first raises and the second prints present, with no value shown.

## Exercise 4: Diagnose a secret declared but not granted to a service.

**Expected answer:** The service lacks the intended mounted input.

**Why:** Check the effective model and service access list before changing file permissions or adding a broad host mount.

**Approach:** Check the service's secrets list in docker compose config: a top-level declaration alone does not mount the file into any service.

**Why this is correct:** Without the grant there is no /run/secrets/demo in that container, so reading it fails.

**A plausible wrong approach:** Changing host file permissions or bind-mounting the folder adds exposure without granting the secret.

**How to verify:** After adding demo under the service's secrets, the file exists in that container only.

## Exercise 5: Explain credential rotation beyond restarting a container.

**Expected answer:** New input must be applied and old authority revoked deliberately.

**Why:** The external service decides which credential remains valid. A process lifecycle event alone cannot establish that policy change.

**Approach:** Separate delivering a new value from making the old one invalid: the service that issued it must revoke it.

**Why this is correct:** Restarting the container picks up the new file but leaves the old credential usable by anyone holding it.

**A plausible wrong approach:** Calling rotation done after a restart leaves the leaked old value working.

**How to verify:** A request using the old credential is rejected by the issuing service after revocation.

## Exercise 6: Write a secret data-flow review.

**Expected evidence:** Source, host protection, service grant, read path, logs, rotation and deletion.

**Why:** Following the bytes through their lifetime reveals exposure paths that a single Compose setting cannot address.

**Approach:** Follow the bytes: where they are created, how the host stores them, which service gets them, how it reads them, what may log them, and how they are rotated and deleted.

**Why this is correct:** Each stage can leak in its own way, which a single compose setting does not cover.

**A plausible wrong approach:** Reviewing only the secrets block misses an error message that prints the value.

**How to verify:** Each stage in the review has a named control and the check that confirmed it.

## Check your transfer

`ENV` values become part of the image configuration, so anyone who can pull or inspect the image reads the password with `docker image inspect`, it travels to every registry and archive the image reaches, and rotating it requires a rebuild. Propose a runtime secret file granted only to the service, read from `/run/secrets` and validated without printing it. Acceptance is that `docker image inspect` and `docker inspect` show no password while the app connects. If the value still appears in either output, it enters through image or environment configuration.
