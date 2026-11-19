# rust-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-025_solution.rs](rust-025_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip owned text:** The unique process-based fixture name and create_new avoid overwriting an existing file. The Unicode text round-trips and the owned path is removed.

**Distinguish bytes from valid text:** A byte buffer is not automatically text, and lossy decoding is a separate policy. Valid UTF-8 decodes while an invalid byte sequence is rejected.

## Task answers

### Task 1: Predict and explain

Trace file-handle and pathname ownership separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The unique process-based fixture name and create_new avoid overwriting an existing file. The Unicode text round-trips and the owned path is removed.

### Task 2: Guided modification

Write two lines with an explicit newline policy.

No separate reference answer has been written for this task. Start from Example B: A byte buffer is not automatically text, and lossy decoding is a separate policy. Valid UTF-8 decodes while an invalid byte sequence is rejected.

### Task 3: Independent construction

Create an owned temporary-file round trip for a report.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let name = format!("report-{}.txt", std::process::id());
    let path = std::env::temp_dir().join(name);
    let report = "pear: 3\napple: 5\n";
    std::fs::write(&path, report)?;
    let restored = std::fs::read_to_string(&path);
    std::fs::remove_file(&path)?;
    assert_eq!(restored?, report);
    assert!(!path.exists());
    Ok(())
}
```

**Observe:** The report reads back unchanged and the temporary file is removed.

The file is removed before the read result is checked, so cleanup happens even when the comparison fails.

### Task 4: Diagnose a defect

Diagnose assuming a relative path resolves against the repository root.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors. Never delete arbitrary user-provided directories. Create_new avoids overwrite but is not a complete untrusted-path security model.

### Task 5: Boundary evidence

Test empty bytes and invalid UTF-8.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip owned text) and Example B (Distinguish bytes from valid text).

### Task 6: Transfer and justify

Design cleanup on every failure path using a small owned temporary-resource wrapper.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **File handle**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A path names a filesystem location relative to a context. It is not the file data and is not permission to access arbitrary storage. A container's temporary worker files are distinct from durable classroom pads and progress. Use an owned temporary location for experiments and retain the user-owned data separately.

Rust resource ownership closes a File when its owner drops, but deleting a temporary pathname is a separate operation. The fixture uses create_new to avoid overwriting another file and removes only its own path. Production persistence adds atomic replacement, recovery and permission policies. A successful round trip does not establish crash durability.

OpenOptions::create_new rejects an existing path. Read and Write traits provide byte operations. write_all handles short writes, and read_to_string validates UTF-8. Drop ends handle ownership while remove_file changes the filesystem namespace.

This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors. Never delete arbitrary user-provided directories. Create_new avoids overwrite but is not a complete untrusted-path security model.

## Review before continuing

Run the reference and confirm that it prints `rust-025: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
