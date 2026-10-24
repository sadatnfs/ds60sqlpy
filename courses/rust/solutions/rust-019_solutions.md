# rust-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-019_solution.rs](rust-019_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return one input view:** The annotation prevents a caller from using the view after a required owner is gone. The output is a borrowed view of the longer input.

**Own a result when lifetime must separate:** A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static. The independent owned result survives the temporary scope.

## Reason through the six tasks

1. **Predict and explain.** Draw the valid-use regions of both inputs and the output.

2. **Guided modification.** Test the tie policy of longer.

3. **Independent construction.** Write a borrowed prefix parser with the narrowest lifetime relationship.

4. **Diagnose a defect.** Try returning a local reference and explain why annotations cannot make it valid.

5. **Boundary evidence.** Test empty inputs and use after one candidate owner leaves scope.

6. **Transfer and justify.** Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner's life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.

`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.

Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
