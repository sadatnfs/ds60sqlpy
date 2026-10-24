# swift-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-024_solution.swift](swift-024_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip in an owned directory:** Random path identity prevents collisions while content and assertions remain deterministic. The UTF-8 bytes round-trip in a uniquely owned location.

**Distinguish file and network locations:** A URL is not permission to access its target; the example classifies values without contacting either target. The two URLs carry different location schemes.

## Reason through the six tasks

1. **Predict and explain.** Trace acquisition, use and defer cleanup.

2. **Guided modification.** Write and read two separate small files under the owned directory.

3. **Independent construction.** Persist a Codable value in a temporary file and validate after reading.

4. **Diagnose a defect.** Diagnose assuming worker temporary files survive container replacement.

5. **Boundary evidence.** Test empty bytes and a missing file as distinct outcomes.

6. **Transfer and justify.** Design a durable app save with atomic replacement and a recoverable previous version.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.

FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.

Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
