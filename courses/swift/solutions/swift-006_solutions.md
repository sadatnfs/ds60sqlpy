# swift-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-006_solution.swift](swift-006_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Classify thresholds:** The ranges express the inclusive boundary and keep out-of-domain values separate. 59 retries, 60 passes and 101 is invalid.

**Use a guard for a required value:** The unwrapped binding is available after the guard because every failing path has returned. The early exit excludes missing and empty values before the valid path.

## Reason through the six tasks

1. **Predict and explain.** Predict each threshold case before running.

2. **Guided modification.** Move the pass boundary to 70 and update adjacent tests.

3. **Independent construction.** Write a three-way classifier for negative, zero and positive quantities.

4. **Diagnose a defect.** Diagnose a closed range used where an exclusive upper bound was intended.

5. **Boundary evidence.** Test both ends of the valid domain and one value beyond each.

6. **Transfer and justify.** Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.

`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.

A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
