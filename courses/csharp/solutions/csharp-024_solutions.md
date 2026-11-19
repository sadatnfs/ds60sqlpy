# csharp-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-024_solution.cs](csharp-024_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Dispose on ordinary scope exit:** Scope exit is the ownership boundary; no garbage-collector timing is needed. The resource is open inside and closed afterward.

**Dispose after failure:** The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten. The controlled exception still triggers cleanup.

## Task answers

### Task 1: Predict and explain

Trace the point at which Dispose runs in each example.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Scope exit is the ownership boundary; no garbage-collector timing is needed. The resource is open inside and closed afterward.

### Task 2: Guided modification

Nest two resources and predict reverse disposal order.

No separate reference answer has been written for this task. Start from Example B: The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten. The controlled exception still triggers cleanup.

### Task 3: Independent construction

Write a helper that reads from a caller-owned stream without closing it.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string ReadAll(Stream stream) {
  var encoding = Encoding.UTF8;
  using var reader = new StreamReader(stream, encoding, leaveOpen: true);
  return reader.ReadToEnd();
}
using var source = new MemoryStream(Encoding.UTF8.GetBytes("data"));
Check(ReadAll(source) == "data", "content read");
Check(source.CanRead, "caller-owned stream stays open");
```

**Observe:** The helper returns data and the caller's stream is still readable afterward.

leaveOpen: true makes the reader dispose only itself, so the stream's owner, the caller, decides when it closes.

### Task 4: Diagnose a defect

Diagnose returning a stream from inside a using scope.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

### Task 5: Boundary evidence

Test cleanup after an exception before normal completion.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Dispose on ordinary scope exit) and Example B (Dispose after failure).

### Task 6: Transfer and justify

Document ownership and leave-open behavior for a parser that wraps a stream reader.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Resource owner**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.

`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.

Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

## Review before continuing

Run the reference and confirm that it prints `csharp-024: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
