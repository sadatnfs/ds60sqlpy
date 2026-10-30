# rust-025: Files, bytes and owned cleanup

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-024`

## Learning objectives

Create an owned temporary-file round trip for a report. Then design cleanup on every failure path using a small owned temporary-resource wrapper.

## Purpose and mental model

A path names a filesystem location relative to a context. It is not the file data and is not permission to access arbitrary storage. A container's temporary worker files are distinct from durable classroom pads and progress. Use an owned temporary location for experiments and retain the user-owned data separately.

Rust resource ownership closes a File when its owner drops, but deleting a temporary pathname is a separate operation. The fixture uses create_new to avoid overwriting another file and removes only its own path. Production persistence adds atomic replacement, recovery and permission policies. A successful round trip does not establish crash durability.

## Vocabulary and concepts

**File handle:** An owned operating-system resource for open file access.

**Path:** A name resolving to a filesystem location.

**Cleanup ownership:** Responsibility to release only resources created or explicitly owned.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

OpenOptions::create_new rejects an existing path. Read and Write traits provide byte operations. write_all handles short writes, and read_to_string validates UTF-8. Drop ends handle ownership while remove_file changes the filesystem namespace.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip owned text

The unique process-based fixture name and create_new avoid overwriting an existing file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::io::{Read, Write};
        let path = std::env::temp_dir().join(format!("rust-lesson-{}-a.txt", std::process::id()));
        let mut file = std::fs::OpenOptions::new()
            .write(true)
            .read(true)
            .create_new(true)
            .open(&path)?;
        file.write_all("café".as_bytes())?;
        drop(file);
        let mut actual = String::new();
        std::fs::File::open(&path)?.read_to_string(&mut actual)?;
        std::fs::remove_file(&path)?;
        assert_eq!(actual, "café");
    }
    println!("rust-025: passed");
    Ok(())
}
```

**Observe:** The Unicode text round-trips and the owned path is removed.

### Example B: Distinguish bytes from valid text

A byte buffer is not automatically text, and lossy decoding is a separate policy.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let valid = String::from_utf8(vec![0x63, 0x61, 0x66, 0xc3, 0xa9])?;
        assert_eq!(valid, "café");
        assert!(String::from_utf8(vec![0xff]).is_err());
    }
    println!("rust-025: passed");
    Ok(())
}
```

**Observe:** Valid UTF-8 decodes while an invalid byte sequence is rejected.

## Exercises

1. **Predict and explain.** Trace file-handle and pathname ownership separately.

2. **Guided modification.** Write two lines with an explicit newline policy.

3. **Independent construction.** Create an owned temporary-file round trip for a report.

4. **Diagnose a defect.** Diagnose assuming a relative path resolves against the repository root.

5. **Boundary evidence.** Test empty bytes and invalid UTF-8.

6. **Transfer and justify.** Design cleanup on every failure path using a small owned temporary-resource wrapper.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors. Never delete arbitrary user-provided directories. Create_new avoids overwrite but is not a complete untrusted-path security model.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain File handle, Path, Cleanup ownership without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-025: Files, bytes and owned cleanup.
Read courses/rust/guides/rust-025.md and courses/rust/lessons/rust-025.rs. Prerequisites: rust-024.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-025_solution.rs and
courses/rust/solutions/rust-025_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
