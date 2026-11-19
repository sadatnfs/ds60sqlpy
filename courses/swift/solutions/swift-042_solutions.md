# swift-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-042_solution.swift](swift-042_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Read the supported version:** Version and payload are inspected independently after decoding. The supported envelope round-trips with two titles.

**Refuse an unknown future schema:** Rejection should preserve recoverable source data rather than silently resetting it. The unsupported document is rejected without modifying its payload.

## Task answers

### Task 1: Predict and explain

Identify the schema and domain validation boundaries.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Version and payload are inspected independently after decoding. The supported envelope round-trips with two titles.

### Task 2: Guided modification

Add a version-one optional field while preserving old decoding behavior.

No separate reference answer has been written for this task. Start from Example B: Rejection should preserve recoverable source data rather than silently resetting it. The unsupported document is rejected without modifying its payload.

### Task 3: Independent construction

Inspect JourneyApp save and load errors with an owned test file.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Schema version** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose replacing an unreadable saved file with an empty default automatically.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

### Task 5: Boundary evidence

Test empty data, malformed data and an unknown future version.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Read the supported version) and Example B (Refuse an unknown future schema).

### Task 6: Transfer and justify

Design a version-one to version-two migration with backup, rollback and verification steps.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Schema version**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.

A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.

Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

## Review before continuing

Run the reference and confirm that it prints `swift-042: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
