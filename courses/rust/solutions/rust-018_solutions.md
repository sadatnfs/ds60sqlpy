# rust-018: explanation and comparison

Executable reference: [rust-018_solution.rs](rust-018_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Retain the result type:** The function moves its chosen result, preserving the concrete type rather than returning an untyped object. The same function returns an integer or owned String.

**Use an associated iterator item:** The consumer knows which values the iterator yields and chooses a compatible aggregation. The iterator's item relationship supports a typed sum.

## Task answers

### Task 1: Predict and explain

Identify each inferred type and required bound.

**Written answer.** In `larger(3, 8)` both arguments are integer literals, so `T` defaults to `i32`, which implements `Ord`. In the second call `T` is `String`, also `Ord`, and the result is compared with a `&str` through `String`'s `PartialEq<&str>`. In Example B, `values.into_iter()` on an array of `i32` yields `Item = i32` by value, and the annotation `let total: i32` selects `i32: Sum<i32>`. `larger(5, 5)` is again `T = i32`.

**Why it is correct.** Each call picks one `T` from its arguments, and the only capability the body needs is `>=`, which `Ord` supplies. The iterator's associated `Item` type is fixed by the array, so only the sum's output type had to be stated.

**Plausible wrong approach.** Thinking `larger(3, String::from("x"))` should work because both types are `Ord` misses that the signature uses one `T` for both parameters; the call is E0308, mismatched types.

**How to verify.** Write `let _: () = larger(3, 8);` and read the E0308 message, which names the inferred type `i32`.

### Task 2: Guided modification

Use larger with a custom ordered value type.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block. Helpers used: `larger`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    #[derive(PartialEq, Eq, PartialOrd, Ord)]
    struct Version {
        major: u32,
        minor: u32,
    }
    let picked = larger(
        Version { major: 1, minor: 9 },
        Version { major: 2, minor: 0 },
    );
    assert_eq!((picked.major, picked.minor), (2, 0));
    let patch = larger(
        Version { major: 1, minor: 2 },
        Version {
            major: 1,
            minor: 10,
        },
    );
    assert_eq!(patch.minor, 10);
    Ok(())
}
```

**Observe:** Version 2.0 beats 1.9, and 1.10 beats 1.2.

Deriving `Ord` compares fields in declaration order, so `major` decides first and `minor` breaks ties. That order happens to match version semantics, and comparing numbers avoids the text trap where `"1.10" < "1.9"`.

**Plausible wrong approach.** Declaring `minor` before `major` still compiles, but the derived order would then rank 1.9 above 2.0.

**How to verify.** Run the block, then swap the two field declarations and see the first assertion fail with `left: (1, 9)`.

### Task 3: Independent construction

Create a generic pair that swaps owned elements.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    struct Pair<T> {
        first: T,
        second: T,
    }
    impl<T> Pair<T> {
        fn swap(self) -> Pair<T> {
            Pair {
                first: self.second,
                second: self.first,
            }
        }
    }
    let pair = Pair {
        first: String::from("left"),
        second: String::from("right"),
    };
    let swapped = pair.swap();
    assert_eq!(swapped.first, "right");
    assert_eq!(swapped.second, "left");
    Ok(())
}
```

**Observe:** Swapping (left, right) gives (right, left) without cloning either String.

swap takes self by value, so it can move both owned elements into the new pair.

### Task 4: Diagnose a defect

Diagnose calling an unavailable method on an unconstrained T.

**Written answer.** The defect is a body that uses a capability the signature never promised, such as `fn size<T>(value: T) -> usize { value.len() }`. The compiler rejects it with E0599, no method named `len` found for type parameter `T`, because a caller could choose `T = i32`. A generic body may use only what its bounds guarantee.

**Why it is correct.** Generic functions are checked once, against their bounds, not separately for each caller's type. That is why a missing bound is reported at the definition rather than at some later call.

**Plausible wrong approach.** Adding `T: Ord` because it is the bound used elsewhere in the lesson does not help: ordering says nothing about length. Take `&str` or `&[U]`, or define a trait that provides `len`.

**How to verify.** Compile the snippet and read E0599. Change the parameter to `value: &[i32]` and it compiles.

### Task 5: Boundary evidence

State tie behavior and test equal values.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block. Helpers used: `larger`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    struct Entry {
        score: u32,
        name: &'static str,
    }
    impl PartialEq for Entry {
        fn eq(&self, other: &Self) -> bool {
            self.score == other.score
        }
    }
    impl Eq for Entry {}
    impl PartialOrd for Entry {
        fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
            Some(self.cmp(other))
        }
    }
    impl Ord for Entry {
        fn cmp(&self, other: &Self) -> std::cmp::Ordering {
            self.score.cmp(&other.score)
        }
    }
    let first = Entry {
        score: 7,
        name: "first",
    };
    let second = Entry {
        score: 7,
        name: "second",
    };
    assert_eq!(larger(first, second).name, "first");
    let low = Entry {
        score: 3,
        name: "low",
    };
    let high = Entry {
        score: 9,
        name: "high",
    };
    assert_eq!(larger(low, high).name, "high");
    assert_eq!(larger(5, 5), 5);
    Ok(())
}
```

**Observe:** On a tie the left argument wins, and a strictly larger right argument still wins.

The policy is that ties return `left`, because the body tests `left >= right`. Equal integers cannot show which one came back, so the test uses a type whose ordering ignores `name`: two entries can be equal under `Ord` yet distinguishable.

**Plausible wrong approach.** Testing ties only with `larger(5, 5)` passes for both `>=` and `>`, so it cannot detect a change in the policy.

**How to verify.** Run the block, then change `>=` to `>` in `larger` and the first assertion fails with `left: "second"`.

### Task 6: Transfer and justify

Choose a generic parameter or associated type for a producer relationship and explain who selects it.

**Judging criteria.** Decide who chooses the produced type. If each producer yields exactly one kind of item, as an iterator yields its `Item`, use an associated type: the implementation selects it once, and callers write `P: Producer` without naming it again. If one producer can sensibly yield several types and the caller picks, use a generic parameter such as `Producer<T>`, accepting that a type may then implement the trait many times and that calls may need annotations. A strong answer names the selector in one sentence and shows a call site under each choice. State one limitation: switching forms later breaks every implementation.

## Mechanism and diagnostic reasoning

Generics retain relationships between input and output types without duplicating source. A trait bound states which operations are available on the parameter. A maximum function needs ordering; a container may need no capability beyond storing its element. Excessive bounds make an API harder to reuse.

Associated types express a type chosen by an implementation, as Iterator does with Item. A generic parameter instead lets a caller choose a type for a use. These are complementary tools. Preserve meaningful relationships rather than erasing everything to a trait object and recovering types through runtime checks.

`T: Ord` constrains a type parameter. Returning T preserves the selected type. `type Item = i32` defines an associated type in an implementation. where clauses can make complex bounds easier to read.

Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.

## Review before continuing

Rebuild Example B (Use an associated iterator item) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
