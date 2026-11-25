# rust-025: Files, bytes and owned cleanup

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-024`

## Learning objectives

Write and read files as bytes or UTF-8, remove owned temporary files on the normal path and use a guard type to cover early returns. The central exercise is task 3: Create an owned temporary-file round trip for a report.

## Purpose and mental model

A path names a filesystem location relative to a context. It is not the file data and is not permission to access arbitrary storage. A container's temporary worker files are distinct from durable classroom pads and progress. Use an owned temporary location for experiments and retain the user-owned data separately.

Rust resource ownership closes a File when its owner drops, but deleting a temporary pathname is a separate operation. The fixture uses create_new to avoid overwriting another file and removes only its own path. Production persistence adds atomic replacement, recovery and permission policies. A successful round trip does not establish crash durability.

## Vocabulary and concepts

**File handle:** An owned operating-system resource for open file access.

**Path:** A name resolving to a filesystem location.

**Cleanup ownership:** Responsibility to release only resources created or explicitly owned.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::env`, `std::fs`, `std::io` and `std::process`. A passing run prints `rust-025: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

OpenOptions::create_new rejects an existing path. Read and Write traits provide byte operations. write_all handles short writes, and read_to_string validates UTF-8. Drop ends handle ownership while remove_file changes the filesystem namespace.

**Reading Example A (Round-trip owned text, code below).** `use std::io::{Read, Write};` brings two traits into scope; `write_all` and `read_to_string` are trait methods and cannot be called unless their trait is imported. `std::env::temp_dir().join(...)` builds an absolute path, and the process id in the file name keeps concurrent runs from colliding. `OpenOptions` collects flags before anything touches the file system: `create_new(true)` makes the open fail if the file already exists rather than truncate someone else's data. Every `?` returns early from `main`, converting the `std::io::Error` into the boxed error type. `"café".as_bytes()` exposes the UTF-8 encoding, five bytes for four characters, and `read_to_string` checks that the bytes read back are valid UTF-8.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors. Never delete arbitrary user-provided directories. Create_new avoids overwrite but is not a complete untrusted-path security model.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Round-trip owned text) before changing anything, and confirm its observation: The Unicode text round-trips and the owned path is removed.
2. Compare Example B (Distinguish bytes from valid text) with Example A and name the first line whose behavior differs. Its observation is: Valid UTF-8 decodes while an invalid byte sequence is rejected.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: This small example removes its file on the normal path; the transfer task adds RAII cleanup for early errors.

Tempting approaches to rule out before you compare:

- **Task 1.** Believing `drop(file)` removes the temporary file leaves a stray file in the temporary directory after every run.
- **Task 2.** Joining with `lines.join("\n")` writes no final newline, so appending a third line later glues it onto `fig,7`.
- **Task 5.** Treating an empty file as an error, or using `from_utf8_lossy` everywhere to avoid errors, either rejects valid data or hides corruption.

## Self-check and next step

Why does Example A open the path with `create_new(true)`, and what does `open` return if the file already exists? Why does it call `drop(file)` before reading the path again, and what would leave the file behind if a `?` between `open` and `remove_file` returned early? Why does `String::from_utf8(vec![0xff])` return an error instead of replacing the byte?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::fs::OpenOptions` documentation](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html) for `create_new` and the error it returns when the path exists.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
