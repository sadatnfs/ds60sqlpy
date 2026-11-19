# web-058: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-058.md`.

## Exercise 1: List the untrusted claims in an uploaded file request.

**Expected answer:** Filename, extension, declared media type, content and size all require a deliberate policy.

**Why:** The filename, extension, declared media type, content and size are all chosen by the client, so each needs a policy.

## Exercise 2: Design a maximum size and allowlist for one required format.

**Expected evidence:** The policy rejects unnecessary formats and enforces a bounded resource budget.

**Why:** An allowlist and a size limit bound risk and resource use, and checking the content's signature catches a renamed file.

## Exercise 3: Write an upload design with separate validation, storage and retrieval boundaries.

**Expected evidence:** Files receive generated names, stay outside executable public paths and have ownership and retention rules.

**Why:** Generated names outside the public directory prevent overwrites and execution, and owner checks protect retrieval.

## Exercise 4: Diagnose concatenating ../../ into a storage path.

**Expected answer:** User input must not determine an unrestricted filesystem location.

**Why:** Traversal sequences escape the intended directory, so user input must never become part of a storage path.

## Exercise 5: Model a timeout after a remote service may have accepted an action.

**Expected evidence:** The outcome is ambiguous; retries need idempotency or reconciliation instead of assuming failure means nothing happened.

**Why:** A timeout does not tell you whether the action happened, so retries need an idempotency key or a reconciliation check.

## Exercise 6: Explain which tests are needed before enabling uploads or email.

**Expected answer:** Exercise actual HTTP upload handling, malformed content, size limits, ownership, cleanup and controlled external-service failure behavior.

**Why:** Real uploads, malformed files, size limits, ownership, cleanup and external-service failures each need direct tests.

## Comparing your worksheet

This lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.
