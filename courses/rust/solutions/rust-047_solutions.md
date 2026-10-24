# rust-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-047_solution.rs](rust-047_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check a bounded algebraic property:** The range avoids overflow, making the mathematical property appropriate to this representation. One hundred bounded pairs satisfy the addition relation.

**Check order and multiplicity separately:** Order alone would not reject a broken implementation that drops duplicates. Sorting establishes order without losing the repeated three.

## Reason through the six tasks

1. **Predict and explain.** State the assumptions making the bounded arithmetic property valid.

2. **Guided modification.** Add a small exhaustive test for checked quantity addition.

3. **Independent construction.** Write a property checking an Arrow filter's output count against its Boolean mask.

4. **Diagnose a defect.** Diagnose a sortedness test that never checks retained values.

5. **Boundary evidence.** Preserve empty, duplicate and all-null regression fixtures.

6. **Transfer and justify.** Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API's ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.

Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.

A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
