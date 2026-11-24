# csharp-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-024_solution.cs](csharp-024_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Dispose on ordinary scope exit:** Scope exit is the ownership boundary; no garbage-collector timing is needed. The resource is open inside and closed afterward.

**Dispose after failure:** The same cleanup contract applies to abnormal control flow, which is where manual release is often forgotten. The controlled exception still triggers cleanup.

## Task answers

### Task 1: Predict and explain

Trace the point at which Dispose runs in each example.

**Written answer.** In Example A, `Dispose` runs at the closing brace of `using (resource) { ... }`, after the `open inside scope` check and before `closed after scope`. In Example B the `throw` leaves the block, `Dispose` runs on the way out, and only then does control reach the empty `catch`.

**Why it is correct.** The compiler expands `using (x) { body }` into `try { body } finally { x?.Dispose(); }`. A `finally` runs whether the block finishes normally or by an exception, so both examples dispose at the same boundary.

**Plausible wrong approach.** Predicting that Example B skips cleanup because the exception jumps straight to `catch` ignores the hidden `finally`. Expecting the garbage collector to close the probe later is also wrong: `Probe` has no finalizer, and nothing else sets `Closed`.

**How to verify.** Change Example B to `catch (InvalidOperationException) { Check(resource.Closed, "disposed before catch"); }`. It passes, proving `Dispose` ran before the handler.

### Task 2: Guided modification

Nest two resources and predict reverse disposal order.

**Written answer.** Add `sealed class Named(string name, List<string> log) : IDisposable { public void Dispose() => log.Add(name); }`, then write `using (var outer = new Named("outer", log)) using (var inner = new Named("inner", log)) { }` and check `log.SequenceEqual(new[] { "inner", "outer" })`.

**Why it is correct.** Nested `using` statements become nested `try`/`finally` blocks, and the inner `finally` runs first. The same reverse order applies to `using var` declarations at the end of their scope.

**Plausible wrong approach.** Expecting declaration order, `outer` then `inner`, would be harmful for real wrappers. If `outer` were a `FileStream` and `inner` a `StreamWriter`, disposing the stream first would make the writer's final flush throw `ObjectDisposedException`.

**How to verify.** Run the check, then rewrite with two `using var` lines in a block and confirm the log is still `inner`, `outer`.

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

**Plausible wrong approach.** Writing `using var reader = new StreamReader(stream, encoding);` without `leaveOpen: true` makes disposing the reader also dispose `source`. `source.CanRead` becomes false and the `caller-owned stream stays open` check throws.

**How to verify.** After the block, set `source.Position = 0;` and check `ReadAll(source) == "data"` a second time. A closed stream would throw `ObjectDisposedException` on the position change.

### Task 4: Diagnose a defect

Diagnose returning a stream from inside a using scope.

**Written answer.** `Stream Open() { using var s = new MemoryStream(bytes); return s; }` hands back a stream that was disposed as the method returned, so the caller's `ReadByte()` throws `ObjectDisposedException`. Return the stream without `using` and document that the caller owns it and must dispose it.

**Why it is correct.** A `using var` disposes at the end of its enclosing scope, which here is the method body. `return` does not cancel the `finally`, so ownership must move to the caller explicitly.

**Plausible wrong approach.** Removing the `using` without telling callers to dispose leaks the resource instead. With a `FileStream` the handle stays open until finalization, so a later `File.Open` with `FileShare.None` on the same path fails with `IOException`.

**How to verify.** With the bug, `Check(Open().CanRead, "usable")` throws. After the fix, `using var s = Open(); Check(s.CanRead && s.ReadByte() >= 0, "usable");` passes.

### Task 5: Boundary evidence

Test cleanup after an exception before normal completion.

**Written answer.** Write `void Work(Probe p, bool fail, ref bool finished) { using (p) { if (fail) throw new InvalidOperationException("fixture"); finished = true; } }`. With `fail = true`, catch the exception and check `p.Closed && !finished`; with `fail = false`, check `p.Closed && finished`.

**Why it is correct.** The two flags separate cleanup from completion. Cleanup must be true on both paths, while completion is true only on the normal one, so the test proves the exception really happened before the work finished.

**Plausible wrong approach.** Calling `p.Dispose()` as the last statement of the block instead of using `using` passes the normal-path test. On the failure path the throw skips that line, so `Closed` stays false; testing only `fail = false` would never show it.

**How to verify.** Run both cases. Then replace `using (p)` with a trailing `p.Dispose();` and confirm the `fail = true` check throws.

### Task 6: Transfer and justify

Document ownership and leave-open behavior for a parser that wraps a stream reader.

**Written answer.** Document: `RowParser(Stream stream, bool leaveOpen = false)` always owns its internal `StreamReader`, and owns the stream only when `leaveOpen` is false. `Dispose` disposes the reader, which closes the stream unless `leaveOpen` is true.

**Why it is correct.** This mirrors `StreamReader`'s own convention, so a caller can predict who closes what. A caller that reads a header with one parser and the body with another passes `leaveOpen: true` to the first.

**Plausible wrong approach.** A parser whose `Dispose` always closes the stream breaks that two-parser pattern: the second parser's first read throws `ObjectDisposedException` because the caller's stream was released by someone that only borrowed it.

**How to verify.** Over a `MemoryStream`, dispose a parser created with `leaveOpen: true` and check `stream.CanRead` is true; repeat with `false` and check it is false.

## Mechanism and diagnostic reasoning

Managed memory collection does not mean every resource can wait for garbage collection. Files, sockets and handles need a clear owner that releases them promptly. IDisposable expresses synchronous cleanup. A using declaration or statement arranges Dispose when control leaves the scope, including exceptions.

Ownership is a contract between caller and callee. If a function receives a stream, it should not close a caller-owned stream unless documented. Multiple wrappers can share an underlying resource, so leave-open options matter. Deterministic cleanup prevents resource exhaustion and also makes tests independent: a later operation should not inherit a locked file from an earlier failure.

`using (var resource = ...) { ... }` scopes lifetime. `using var resource = ...` disposes at the end of the containing scope. `await using` supports IAsyncDisposable when cleanup itself is asynchronous.

Dispose does not automatically make an object safe for concurrent callers. Never rely on finalizer timing for a lock or file release. Releasing a borrowed resource violates its caller ownership.

## Review before continuing

Run the reference and confirm that it prints `csharp-024: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
