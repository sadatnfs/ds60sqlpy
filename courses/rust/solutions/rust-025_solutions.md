# rust-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-025_solution.rs](rust-025_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip owned text:** The unique process-based fixture name and create_new avoid overwriting an existing file. The Unicode text round-trips and the owned path is removed.

**Distinguish bytes from valid text:** A byte buffer is not automatically text, and lossy decoding is a separate policy. Valid UTF-8 decodes while an invalid byte sequence is rejected.

## Task answers

### Task 1: Predict and explain

Trace file-handle and pathname ownership separately.

**Written answer.** `file` owns the operating system handle; `drop(file)` flushes nothing extra but closes it, and a second `File::open` creates a new temporary handle that is dropped at the end of that statement. `path` is a `PathBuf` that owns only the name. Dropping `path` deletes nothing; the directory entry exists until `std::fs::remove_file(&path)` runs.

**Why it is correct.** Handle lifetime and file existence are separate resources. Ownership closes handles automatically, but removing a name is a filesystem operation that only an explicit call (or a guard's `Drop`) performs.

**Plausible wrong approach.** Believing `drop(file)` removes the temporary file leaves a stray file in the temporary directory after every run.

**How to verify.** Comment out the `remove_file` line, run Example A, then check that the file still exists with `assert!(path.exists())`.

### Task 2: Guided modification

Write two lines with an explicit newline policy.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::io::Write;
    let name = format!("rust-lesson-{}-lines.txt", std::process::id());
    let path = std::env::temp_dir().join(name);
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)?;
    for line in ["pear,3", "fig,7"] {
        writeln!(file, "{line}")?;
    }
    drop(file);
    let text = std::fs::read_to_string(&path);
    std::fs::remove_file(&path)?;
    let text = text?;
    assert_eq!(text, "pear,3\nfig,7\n");
    assert!(!text.contains('\r'));
    assert_eq!(text.lines().count(), 2);
    Ok(())
}
```

**Observe:** The file holds exactly pear,3 and fig,7, each followed by a single LF byte, and the path is removed.

The policy is one `\n` after every line, including the last. `writeln!` writes `\n` on every platform, never `\r\n`, so the bytes are the same on Linux and Windows. Reading is kept as a `Result` until after `remove_file`, so a read failure cannot skip the cleanup.

**Plausible wrong approach.** Joining with `lines.join("\n")` writes no final newline, so appending a third line later glues it onto `fig,7`.

**How to verify.** Run the block, then switch `writeln!` to `write!` and the first assertion fails with `pear,3fig,7`.

### Task 3: Independent construction

Create an owned temporary-file round trip for a report.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let name = format!("report-{}.txt", std::process::id());
    let path = std::env::temp_dir().join(name);
    let report = "pear: 3\napple: 5\n";
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)?;
    std::io::Write::write_all(&mut file, report.as_bytes())?;
    drop(file);
    let restored = std::fs::read_to_string(&path);
    std::fs::remove_file(&path)?;
    assert_eq!(restored?, report);
    assert!(!path.exists());
    Ok(())
}
```

**Observe:** The report reads back unchanged and the temporary file is removed.

`create_new(true)` refuses to open a path that already exists, so the round trip never truncates someone else's file, which `std::fs::write` would do. The file is removed before the read result is checked, so cleanup happens even when the comparison fails.

### Task 4: Diagnose a defect

Diagnose assuming a relative path resolves against the repository root.

**Written answer.** The defect is `std::fs::read_to_string("data/report.txt")` written on the assumption that it means the repository's `data` folder. A relative path is resolved against the process's current working directory, which is wherever the program was launched: a terminal's directory, an IDE setting, or the worker's scratch directory. Build paths from an explicit base such as a command-line argument or `std::env::temp_dir()`.

**Why it is correct.** Neither the source file's location nor the project root is part of path resolution. Only the process working directory is, and the caller controls it.

**Plausible wrong approach.** Fixing it by hard-coding an absolute path from your own machine works only there and can point at another user's files elsewhere.

**How to verify.** Print `std::env::current_dir()?` in the pad and compare it with the folder you assumed.

### Task 5: Boundary evidence

Test empty bytes and invalid UTF-8.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::io::Read;
    let name = format!("rust-lesson-{}-empty.bin", std::process::id());
    let path = std::env::temp_dir().join(name);
    let file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)?;
    drop(file);
    let mut bytes = Vec::new();
    let read = std::fs::File::open(&path).and_then(|mut f| f.read_to_end(&mut bytes));
    std::fs::remove_file(&path)?;
    assert_eq!(read?, 0);
    assert_eq!(String::from_utf8(bytes)?, "");
    assert!(String::from_utf8(vec![0x63, 0xc3]).is_err());
    assert_eq!(String::from_utf8_lossy(&[0x63, 0xff]), "c\u{fffd}");
    Ok(())
}
```

**Observe:** An empty file reads zero bytes and decodes to empty text, a truncated two-byte sequence is rejected, and lossy decoding replaces the invalid byte with U+FFFD.

Empty input is valid UTF-8, so it decodes cleanly. `0xc3` starts a two-byte character that never finishes, so strict decoding fails, while `from_utf8_lossy` succeeds only by changing the data. The read result is held until the path is removed, so a failed read does not leave the file behind.

**Plausible wrong approach.** Treating an empty file as an error, or using `from_utf8_lossy` everywhere to avoid errors, either rejects valid data or hides corruption.

**How to verify.** Run the block, then replace `vec![0x63, 0xc3]` with `vec![0x63, 0xc3, 0xa9]` and the rejection assertion fails because the bytes now spell `cé`.

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
