# csharp-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-002_solution.cs](csharp-002_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Division depends on operand types:** Converting after integer division would preserve the already truncated result. Operand conversion must happen before division. The integer result is 3 and the floating result is 3.5.

**Parse an external representation:** The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value. 42 parses successfully; words fail without an exception.

## Reason through the six tasks

1. **Predict and explain.** Predict the type and value of 7/2, 7/2.0 and (double)(7/2).

2. **Guided modification.** Change the operands to 8 and 2 and explain why that input hides the truncation difference.

3. **Independent construction.** Write a TryParse-based validator accepting only nonnegative whole-number quantities.

4. **Diagnose a defect.** Diagnose a conversion performed after integer division. Produce a fractional counterexample.

5. **Boundary evidence.** Test empty text, zero, a negative number and a number outside the int range.

6. **Transfer and justify.** Design an input boundary for a percentage and document its accepted textual and numeric ranges.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.

`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.

An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
