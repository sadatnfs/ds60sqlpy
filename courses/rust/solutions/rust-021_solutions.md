# rust-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-021_solution.rs](rust-021_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe mutable capture:** The scope makes the exclusive captured access visible. The closure updates its borrowed accumulator before the borrow ends.

**Move owned data into a closure:** Returning the owned capture makes this closure consuming rather than indefinitely repeatable. The closure transfers its captured String to the caller once.

## Reason through the six tasks

1. **Predict and explain.** Identify capture mode and calling capability in each example.

2. **Guided modification.** Write a pure repeatable closure capturing an immutable factor.

3. **Independent construction.** Implement a helper accepting FnMut for repeated transformations.

4. **Diagnose a defect.** Diagnose attempting to call a consuming closure twice.

5. **Boundary evidence.** Test a closure with no captures and one capturing a borrowed reference.

6. **Transfer and justify.** Choose capture ownership for work that will run on another thread.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.

`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.

Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
