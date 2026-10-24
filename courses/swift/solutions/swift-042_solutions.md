# swift-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-042_solution.swift](swift-042_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Read the supported version:** Version and payload are inspected independently after decoding. The supported envelope round-trips with two titles.

**Refuse an unknown future schema:** Rejection should preserve recoverable source data rather than silently resetting it. The unsupported document is rejected without modifying its payload.

## Reason through the six tasks

1. **Predict and explain.** Identify the schema and domain validation boundaries.

2. **Guided modification.** Add a version-one optional field while preserving old decoding behavior.

3. **Independent construction.** Inspect JourneyApp save and load errors with an owned test file.

4. **Diagnose a defect.** Diagnose replacing an unreadable saved file with an empty default automatically.

5. **Boundary evidence.** Test empty data, malformed data and an unknown future version.

6. **Transfer and justify.** Design a version-one to version-two migration with backup, rollback and verification steps.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.

A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.

Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
