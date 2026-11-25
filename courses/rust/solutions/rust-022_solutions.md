# rust-022: explanation and comparison

Executable reference: [rust-022_solution.rs](rust-022_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Preserve a domain category:** A caller can decide from the type rather than inspect a fragile message substring. Negative and malformed inputs remain separate variants.

**Render a safe message:** Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure. The message explains the rule without repeating raw input.

## Task answers

### Task 1: Predict and explain

Match each failure to its domain variant.

**Written answer.** `"bad"` fails `parse`, and `map_err(|_| InputError::Malformed)` turns that into `Malformed` before `?` returns. `"-1"` parses to `-1`, then the sign test returns `Err(InputError::Negative)`. `"3"` passes both stages and returns `Ok(3)`. Empty text and numbers outside the `i32` range also fail `parse`, so they become `Malformed` as well.

**Why it is correct.** The variant is chosen at the stage that detects the problem: syntax failures in `map_err`, the domain rule in the explicit branch. The caller then decides from the variant, as Example A does with `matches!`.

**Plausible wrong approach.** Mapping `"-1"` to `Malformed` because it contains a sign confuses text shape with the domain rule, since `i32` parses negative numbers normally.

**How to verify.** Add `assert!(matches!(validated(""), Err(InputError::Malformed)));` to Example A and run it.

### Task 2: Guided modification

Add a maximum-quantity category.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block. Helpers used: `validated`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    #[derive(Debug)]
    enum QuantityError {
        Input(InputError),
        TooLarge { max: i32 },
    }
    impl From<InputError> for QuantityError {
        fn from(error: InputError) -> Self {
            Self::Input(error)
        }
    }
    fn bounded(text: &str, max: i32) -> Result<i32, QuantityError> {
        let value = validated(text)?;
        if value > max {
            return Err(QuantityError::TooLarge { max });
        }
        Ok(value)
    }
    assert_eq!(bounded("40", 50).unwrap(), 40);
    assert!(matches!(
        bounded("51", 50),
        Err(QuantityError::TooLarge { max: 50 })
    ));
    let negative = bounded("-1", 50);
    assert!(matches!(
        negative,
        Err(QuantityError::Input(InputError::Negative))
    ));
    let malformed = bounded("x", 50);
    assert!(matches!(
        malformed,
        Err(QuantityError::Input(InputError::Malformed))
    ));
    Ok(())
}
```

**Observe:** 40 is accepted, 51 is TooLarge with the limit 50, and the negative and malformed cases keep their original InputError variants.

The new category wraps the existing one rather than editing it, and `impl From<InputError>` lets `?` convert automatically. The limit is a value, not a constant baked into the message, so the caller can report it without parsing text.

**Plausible wrong approach.** Returning `Err(InputError::Negative)` for oversized values because it is the nearest existing variant compiles and shows a false message saying the quantity must be nonnegative.

**How to verify.** Run the block. Remove the `From` impl and the `?` line fails with E0277, `?` couldn't convert the error to `QuantityError`.

### Task 3: Independent construction

Define a custom error for an importer with syntax and storage boundaries.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is `if error.to_string().contains("nonnegative") { retry_with_absolute_value() }`. The branch depends on display text written for people, so rewording the message or translating it silently changes program behavior. Match the variant instead: `if let Err(InputError::Negative) = result`.

**Why it is correct.** `Display` is presentation and the enum is the contract. Variants are checked by the compiler; a substring test still compiles after the message changes and just stops matching.

**Plausible wrong approach.** Comparing the whole string with `==` instead of `contains` is stricter but has the same dependency on wording.

**How to verify.** Change the `Negative` message to `quantity must be zero or more`: the string branch stops firing with no compiler error, while a `matches!` test still passes.

### Task 5: Boundary evidence

Test zero, malformed and out-of-range text.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block. Helpers used: `validated`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(validated("0").unwrap(), 0);
    assert!(matches!(validated("abc"), Err(InputError::Malformed)));
    assert!(matches!(validated(""), Err(InputError::Malformed)));
    assert!(matches!(
        validated("2147483648"),
        Err(InputError::Malformed)
    ));
    assert!(matches!(
        validated("-2147483648"),
        Err(InputError::Negative)
    ));
    assert!(matches!(
        validated("-2147483649"),
        Err(InputError::Malformed)
    ));
    Ok(())
}
```

**Observe:** Zero is accepted, letters and empty text are malformed, i32::MIN is negative, and values just outside the i32 range in either direction are malformed.

Zero sits on the accepted side of `value < 0`. Out-of-range text never becomes a number, so it lands in `Malformed` rather than in a range category; a real importer might add one, as task 2 did for the upper limit.

**Plausible wrong approach.** Expecting `"-2147483649"` to be `Negative` assumes the sign is checked before the range. Parsing runs first and fails, so the domain check never sees it.

**How to verify.** Run the block, then change `value < 0` to `value <= 0` and the first assertion fails.

### Task 6: Transfer and justify

Choose which layer translates an internal error into a public response and what context it may expose.

**Judging criteria.** A strong design keeps detailed variants such as `InputError::Malformed` inside the domain and translates them once, at the outermost layer that knows the audience, such as an HTTP handler or the binary's `main`. That layer maps each variant to a public category and a safe message, logs the full cause chain with a correlation identity, and never echoes raw input, paths or library error text. State one limitation: the translation point must change whenever a variant is added, which an exhaustive `match` makes visible.

## Mechanism and diagnostic reasoning

A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.

Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.

A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

## Review before continuing

Rebuild Example B (Render a safe message) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
