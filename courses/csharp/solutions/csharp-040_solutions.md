# csharp-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-040_solution.cs](csharp-040_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Inject a deterministic clock:** The domain behavior does not depend on the machine clock during the test. The result uses the supplied instant.

**Preserve a core validation rule:** Dependency variation should not weaken the invariant owned by the domain. A different clock does not bypass identity validation.

## Task answers

### Task 1: Predict and explain

Identify policy and mechanism in the service.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The domain behavior does not depend on the machine clock during the test. The result uses the supplied instant.

### Task 2: Guided modification

Supply a second fixed clock and predict the changed timestamp.

No separate reference answer has been written for this task. Start from Example B: Dependency variation should not weaken the invariant owned by the domain. A different clock does not bypass identity validation.

### Task 3: Independent construction

Extract the inventory aggregation into a transport-independent core.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
(int Total, int Rejected) Aggregate(IEnumerable<int> quantities) {
  int total = 0;
  int rejected = 0;
  foreach (int quantity in quantities) {
    if (quantity < 0) {
      rejected++;
    } else {
      total = checked(total + quantity);
    }
  }
  return (total, rejected);
}
var result = Aggregate(new[] { 2, -1, 3 });
Check(result.Total == 5 && result.Rejected == 1, "core aggregation");
```

**Observe:** Quantities 2, -1 and 3 aggregate to total 5 with one rejection.

The core takes plain values and returns plain values; it knows nothing about files, HTTP or the console, so any adapter can call it.

### Task 4: Diagnose a defect

Diagnose a domain method reading the system clock internally despite accepting a clock.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

### Task 5: Boundary evidence

Test empty identity and a fixed instant around a date boundary.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Inject a deterministic clock) and Example B (Preserve a core validation rule).

### Task 6: Transfer and justify

Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Domain core**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.

A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.

A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

## Review before continuing

Run the reference and confirm that it prints `csharp-040: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
