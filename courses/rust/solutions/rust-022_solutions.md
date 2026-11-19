# rust-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-022_solution.rs](rust-022_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve a domain category:** A caller can decide from the type rather than inspect a fragile message substring. Negative and malformed inputs remain separate variants.

**Render a safe message:** Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure. The message explains the rule without repeating raw input.

## Task answers

### Task 1: Predict and explain

Match each failure to its domain variant.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A caller can decide from the type rather than inspect a fragile message substring. Negative and malformed inputs remain separate variants.

### Task 2: Guided modification

Add a maximum-quantity category.

No separate reference answer has been written for this task. Start from Example B: Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure. The message explains the rule without repeating raw input.

### Task 3: Independent construction

Define a custom error for an importer with syntax and storage boundaries.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    #[derive(Debug)]
    enum ImportError {
        Syntax { line: usize },
        Storage(std::io::Error),
    }
    impl std::fmt::Display for ImportError {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            match self {
                Self::Syntax { line } => write!(f, "syntax error on line {line}"),
                Self::Storage(_) => write!(f, "storage failed"),
            }
        }
    }
    impl std::error::Error for ImportError {
        fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
            match self {
                Self::Syntax { .. } => None,
                Self::Storage(cause) => Some(cause),
            }
        }
    }
    use std::error::Error;
    let syntax = ImportError::Syntax { line: 3 };
    assert_eq!(syntax.to_string(), "syntax error on line 3");
    assert!(syntax.source().is_none());
    let cause = std::io::Error::other("disk full");
    let storage = ImportError::Storage(cause);
    assert_eq!(storage.source().unwrap().to_string(), "disk full");
    Ok(())
}
```

**Observe:** The syntax error names line 3; the storage error keeps the disk full cause reachable through source.

Separate variants let callers fix input or retry storage, and source preserves the underlying io::Error instead of flattening it into a string.

### Task 4: Diagnose a defect

Diagnose branching on a translated message string.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

### Task 5: Boundary evidence

Test zero, malformed and out-of-range text.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve a domain category) and Example B (Render a safe message).

### Task 6: Transfer and justify

Choose which layer translates an internal error into a public response and what context it may expose.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Error enum**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.

Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.

A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

## Review before continuing

Run the reference and confirm that it prints `rust-022: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
