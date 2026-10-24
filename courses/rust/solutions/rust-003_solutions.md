# rust-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-003_solution.rs](rust-003_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Choose a visible overflow policy:** The choice is semantic and should not depend on a compiler optimization setting. The same boundary produces absence, zero or 255 under three distinct policies.

**Keep numeric units explicit:** Integer smallest units avoid accidental decimal approximation in this bounded pricing example. Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

## Reason through the six tasks

1. **Predict and explain.** Predict the three overflow policies.

2. **Guided modification.** Repeat the investigation with subtraction at zero.

3. **Independent construction.** Write a checked quantity-total calculation returning an explicit failure.

4. **Diagnose a defect.** Diagnose relying on debug-mode overflow behavior in production logic.

5. **Boundary evidence.** Test zero, maximum and one beyond an accepted application range.

6. **Transfer and justify.** Choose numeric representation, units and rounding rules for a pricing contract.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Fixed-width integers have finite ranges. Rust provides explicit checked, wrapping, saturating and overflowing arithmetic so an API can state what happens at a boundary. Do not rely on differences between debug and optimized overflow settings for business correctness. Choose the intended policy directly.

Floating-point arithmetic approximates many decimal fractions. A tolerance should reflect scale and numerical error, not hide a unit mismatch. Money often needs an integer smallest-unit representation or a separately prepared decimal library with a documented rounding policy. The standard library does not make every numerical domain exact automatically.

`checked_add` returns Option and reports overflow as None. `wrapping_add` performs modular arithmetic. `saturating_add` stays at the limit. An explicit integer type makes the tested range unambiguous.

Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
