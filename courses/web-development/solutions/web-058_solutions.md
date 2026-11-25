# web-058: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-058.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: List the untrusted claims in an uploaded file request.

**Expected answer:** Filename, extension, declared media type, content and size all require a deliberate policy.

**Approach:** List every field the client supplies in the upload: original name, extension, declared type, size and the content bytes.

**Why:** The filename, extension, declared media type, content and size are all chosen by the client, so each needs a policy.

**Plausible wrong approach:** Trusting the `type` value in `$_FILES` fails because the browser or a script sets it, and it can claim any media type.

**How to verify:** Your list marks all five items as client controlled and names a server check for each.

## Exercise 2: Design a maximum size and allowlist for one required format.

**Expected evidence:** The policy rejects unnecessary formats and enforces a bounded resource budget.

**Approach:** Pick one format such as PNG, set a byte limit such as 2 MB, and check both the size and the file's actual signature.

**Why:** An allowlist and a size limit bound risk and resource use, and checking the content's signature catches a renamed file.

**Plausible wrong approach:** Allowing any file whose name ends in .png fails because renaming a script to image.png passes that check.

**How to verify:** Your policy rejects a renamed text file and a 5 MB PNG, and accepts a small real PNG.

## Exercise 3: Write an upload design with separate validation, storage and retrieval boundaries.

**Expected evidence:** Files receive generated names, stay outside executable public paths and have ownership and retention rules.

**Approach:** Describe three steps: validate the upload, store bytes under a generated name outside public, and serve through a handler that checks the owner.

**Why:** Generated names outside the public directory prevent overwrites and execution, and owner checks protect retrieval.

**Plausible wrong approach:** Serving stored files directly from a public folder fails because ownership checks and content type control are skipped.

**How to verify:** Your design shows no path from a public URL to the storage folder that skips the download handler.

## Exercise 4: Diagnose concatenating ../../ into a storage path.

**Expected answer:** User input must not determine an unrestricted filesystem location.

**Approach:** Generate the stored name on the server and never join user input into the directory path.

**Why:** Traversal sequences escape the intended directory, so user input must never become part of a storage path.

**Plausible wrong approach:** Removing only the first `../` from the name fails because nested sequences such as `....//` can still produce a traversal.

**How to verify:** A name containing `../../config.php` has no effect on where the file is stored.

## Exercise 5: Model a timeout after a remote service may have accepted an action.

**Expected evidence:** The outcome is ambiguous; retries need idempotency or reconciliation instead of assuming failure means nothing happened.

**Approach:** Record the attempt as pending with an idempotency key, and resolve the unknown outcome by querying the remote service or retrying with the same key.

**Why:** A timeout does not tell you whether the action happened, so retries need an idempotency key or a reconciliation check.

**Plausible wrong approach:** Marking the action failed and sending a new request fails because the first one may have succeeded, so the user gets two charges.

**How to verify:** Your model retries with the same key and shows the remote side ignoring the duplicate.

## Exercise 6: Explain which tests are needed before enabling uploads or email.

**Expected answer:** Exercise actual HTTP upload handling, malformed content, size limits, ownership, cleanup and controlled external-service failure behavior.

**Approach:** List tests that need the real stack: multipart uploads, oversized and malformed files, ownership on download, cleanup and remote failures.

**Why:** Real uploads, malformed files, size limits, ownership, cleanup and external-service failures each need direct tests.

**Plausible wrong approach:** Testing the validator with a fake `$_FILES` array only fails because `move_uploaded_file` rejects files that did not arrive through HTTP upload.

**How to verify:** Your list includes at least one test that sends a real multipart request to a local server you own.

## Comparing your worksheet

Compare your boundaries with the solution's: where size and type are checked, who chooses the stored name and how retrieval authorizes the reader. The optional lab does not accept uploads, so your evidence here is the design and the tests you list, not a running service.

This lesson has no executable reference ([worksheet rules](../STUDY-GUIDE.md#worksheets)).
