# rust-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-018_solution.rs](rust-018_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain the result type:** The function moves its chosen result, preserving the concrete type rather than returning an untyped object. The same function returns an integer or owned String.

**Use an associated iterator item:** The consumer knows which values the iterator yields and chooses a compatible aggregation. The iterator's item relationship supports a typed sum.

## Task answers

### Task 1: Predict and explain

Identify each inferred type and required bound.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The function moves its chosen result, preserving the concrete type rather than returning an untyped object. The same function returns an integer or owned String.

### Task 2: Guided modification

Use larger with a custom ordered value type.

No separate reference answer has been written for this task. Start from Example B: The consumer knows which values the iterator yields and chooses a compatible aggregation. The iterator's item relationship supports a typed sum.

### Task 3: Independent construction

Create a generic pair that swaps owned elements.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.

### Task 5: Boundary evidence

State tie behavior and test equal values.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Retain the result type) and Example B (Use an associated iterator item).

### Task 6: Transfer and justify

Choose a generic parameter or associated type for a producer relationship and explain who selects it.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Generic parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Generics retain relationships between input and output types without duplicating source. A trait bound states which operations are available on the parameter. A maximum function needs ordering; a container may need no capability beyond storing its element. Excessive bounds make an API harder to reuse.

Associated types express a type chosen by an implementation, as Iterator does with Item. A generic parameter instead lets a caller choose a type for a use. These are complementary tools. Preserve meaningful relationships rather than erasing everything to a trait object and recovering types through runtime checks.

`T: Ord` constrains a type parameter. Returning T preserves the selected type. `type Item = i32` defines an associated type in an implementation. where clauses can make complex bounds easier to read.

Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.

## Review before continuing

Run the reference and confirm that it prints `rust-018: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
