# csharp-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-045_solution.cs](csharp-045_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Inspect declared metadata:** Runtime lookup needs an absence policy even when the programmer expects a member to exist. The known property is an int and the missing property is absent.

**Prefer typed access for a fixed contract:** A statically known relationship gives the compiler and deployment tools more information. The fixed projection needs no string-based member lookup.

## Reason through the six tasks

1. **Predict and explain.** Compare compile-time and runtime checking in the two examples.

2. **Guided modification.** Inspect a different known property and handle absence explicitly.

3. **Independent construction.** Replace string-based access in a small report with a typed projection.

4. **Diagnose a defect.** Diagnose assuming dynamic reflection will remain available after trimming.

5. **Boundary evidence.** Test an absent member and an unexpected member type.

6. **Transfer and justify.** Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.

`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.

Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
