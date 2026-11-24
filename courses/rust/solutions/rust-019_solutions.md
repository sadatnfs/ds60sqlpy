# rust-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-019_solution.rs](rust-019_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return one input view:** The annotation prevents a caller from using the view after a required owner is gone. The output is a borrowed view of the longer input.

**Own a result when lifetime must separate:** A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static. The independent owned result survives the temporary scope.

## Task answers

### Task 1: Predict and explain

Draw the valid-use regions of both inputs and the output.

**Written answer.** `left` and `right` are valid from their `let` lines to the end of the block. The call `longer(&left, &right)` borrows both, and because the signature gives the result the same `'a`, the returned `&str` may be used only while both borrows are valid. Here it is used once, inside the `assert_eq!`, and its region ends there, so both owners stay free afterward.

**Why it is correct.** A single lifetime on all three references asks the compiler for a region inside both inputs' regions. The caller decides where the result is used, and the borrow checker confirms that this use falls within that region.

**Plausible wrong approach.** Drawing the output region as the whole region of `right` because the longer string happens to be `right` ignores that the signature cannot know which input is returned.

**How to verify.** After the assertion add `let view = longer(&left, &right); drop(left); println!("{view}");` and read E0505, cannot move out of `left` because it is borrowed.

### Task 2: Guided modification

Test the tie policy of longer.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file. It uses `longer` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let first = String::from("pear");
    let second = String::from("plum");
    let chosen = longer(&first, &second);
    assert!(std::ptr::eq(chosen, first.as_str()));
    assert_eq!(longer("fig", "kiwi"), "kiwi");
    assert_eq!(longer("", ""), "");
    Ok(())
}
```

**Observe:** With two four-byte inputs the result is the very slice of `first`, and a strictly longer right input still wins.

`longer` uses `>=`, so ties return `left`. Comparing text with `assert_eq!` cannot see that, since `pear` and `plum` differ but tie on length; `std::ptr::eq` compares the slice addresses and proves which owner the view borrows.

**Plausible wrong approach.** Testing with `longer("pear", "pear")` and `assert_eq!` passes whichever argument is returned, so it says nothing about the policy.

**How to verify.** Run the block, then change `>=` to `>` in `longer` and the `ptr::eq` assertion fails.

### Task 3: Independent construction

Write a borrowed prefix parser with the narrowest lifetime relationship.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn split_prefix<'a>(text: &'a str, prefix: &str) -> Option<&'a str> {
        text.strip_prefix(prefix)
    }
    let line = String::from("qty:42");
    let rest = {
        let prefix = String::from("qty:");
        split_prefix(&line, &prefix)
    };
    assert_eq!(rest, Some("42"));
    Ok(())
}
```

**Observe:** The rest of qty:42 is Some("42"), still usable after the prefix String is dropped.

Only text shares the result's lifetime 'a; prefix gets its own shorter lifetime, so the caller can drop it while keeping the result.

### Task 4: Diagnose a defect

Try returning a local reference and explain why annotations cannot make it valid.

**Written answer.** The defect is `fn label<'a>() -> &'a str { let local = String::from("draft"); &local }`. It fails with E0515, cannot return reference to local variable `local`: the String is dropped when the function returns, so any reference to it would dangle. The annotation only names a relationship, and nothing the caller passes in owns the data.

**Why it is correct.** Lifetimes are checked, not granted. A returned reference must borrow from something that outlives the call, which means an input or static data, and `local` is neither.

**Plausible wrong approach.** Writing `-> &'static str` instead changes the promise without changing the storage, so it fails with the same E0515.

**How to verify.** Compile the snippet and read E0515. Return `String` instead and it compiles, as Example B does.

### Task 5: Boundary evidence

Test empty inputs and use after one candidate owner leaves scope.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file. It uses `longer` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(longer("", "x"), "x");
    assert_eq!(longer("x", ""), "x");
    let outer = String::from("outer value");
    let kept = {
        let inner = String::from("in");
        longer(&outer, &inner).to_owned()
    };
    assert_eq!(kept, "outer value");
    Ok(())
}
```

**Observe:** An empty input loses to any nonempty one on either side, and the owned copy survives after `inner` leaves scope.

Returning `longer(&outer, &inner)` itself from the block is rejected with E0597, `inner` does not live long enough, even though the longer value is `outer`. The signature ties the result to both inputs, so the shorter-lived owner limits it; `to_owned` makes an independent String instead.

**Plausible wrong approach.** Assuming the borrow checker sees at run time that `outer` won and allows the view to escape treats lifetimes as a dynamic property. They are decided from the signature alone.

**How to verify.** Run the block. Remove `.to_owned()` and read E0597 naming `inner`.

### Task 6: Transfer and justify

Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Lifetime parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner's life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.

`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.

Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

## Review before continuing

Run the reference and confirm that it prints `rust-019: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
