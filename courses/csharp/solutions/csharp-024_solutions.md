# csharp-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-024_solution.cs](csharp-024_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Dispose on ordinary scope exit:** Scope exit is the ownership boundary; no garbage-collector timing is needed. The resource is open inside and closed afterward.

**Dispose after failure:** The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten. The controlled exception still triggers cleanup.

## Reason through the six tasks

1. **Predict and explain.** Trace the point at which Dispose runs in each example.

2. **Guided modification.** Nest two resources and predict reverse disposal order.

3. **Independent construction.** Write a helper that reads from a caller-owned stream without closing it.

4. **Diagnose a defect.** Diagnose returning a stream from inside a using scope.

5. **Boundary evidence.** Test cleanup after an exception before normal completion.

6. **Transfer and justify.** Document ownership and leave-open behavior for a parser that wraps a stream reader.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.

`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.

Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
