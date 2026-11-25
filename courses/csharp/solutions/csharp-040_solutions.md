# csharp-040: explanation and comparison

Reference program: [csharp-040_solution.cs](csharp-040_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Inject a deterministic clock:** The domain behavior does not depend on the machine clock during the test. The result uses the supplied instant.

**Preserve a core validation rule:** Dependency variation should not weaken the invariant owned by the domain. A different clock does not bypass identity validation.

## Task answers

### Task 1: Predict and explain

Identify policy and mechanism in the service.

**Written answer.** In `StampService` the policy is the rule that an identity must be present and that a stamp is the instant in round-trip `O` format, a colon and the identity. The mechanism is where the instant comes from: `IClock` is the port, and `FixedClock` here or a system clock in production is the adapter. Example A changes only the mechanism and the format rule still applies; Example B shows a different clock cannot bypass the identity rule.

**Why it is correct.** Policy is what the business would argue about; mechanism is how the program reaches the outside world. Keeping them apart lets you test the policy without real time and change the clock without touching the rule.

**Plausible wrong approach.** Calling the `FixedClock` record part of the domain policy confuses a test adapter with the rule it serves.

**How to verify.** List which lines would change if the stamp format changed (policy) and which would change if time came from a network service (mechanism); no line should be on both lists.

### Task 2: Guided modification

Supply a second fixed clock and predict the changed timestamp.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var utc = TimeSpan.Zero;
var instant = new DateTimeOffset(2025, 6, 15, 9, 30, 0, utc);
var service = new StampService(new FixedClock(instant));
string stamp = service.Stamp("order-7");
string expected = "2025-06-15T09:30:00.0000000+00:00:order-7";
Check(stamp == expected, "predicted stamp");
var epoch = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));
Check(epoch.Stamp("order-7") != stamp, "only the clock changed");
```

**Observe:** The second clock produces 2025-06-15T09:30:00.0000000+00:00:order-7, written down before running.

Because the clock is injected, the timestamp is fully determined by the supplied instant, and the round-trip `O` format always shows seven fractional digits and the offset. That makes the full string predictable, so the check compares it exactly. The same identity with the Unix epoch clock produces a different stamp, which shows the clock is the only input that changed.

**Plausible wrong approach.** Predicting `2025-06-15T09:30:00Z` forgets that `DateTimeOffset` formats its offset as `+00:00`, and comparing only `StartsWith("2025")` would not catch a wrong format.

**How to verify.** Change the instant to 2025-06-15 09:30 at offset +02:00 and predict the new string before running.

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

**Written answer.** A method such as `public string Stamp(string id) => DateTimeOffset.UtcNow.ToString("O") + ":" + id;` inside a class that received `IClock clock` ignores its dependency. Every test that supplies a `FixedClock` still passes for the identity rule, but the timestamp is now the real time, so any test that checks the stamp becomes flaky or has to be loosened. Fix it by reading `clock.Now` everywhere in the domain and leaving `DateTimeOffset.UtcNow` only in the production `IClock` adapter.

**Why it is correct.** Accepting a dependency documents a promise that the method's results depend only on what was injected. Reaching around it breaks that promise silently.

**Plausible wrong approach.** Making the test tolerant, for example checking only that the stamp is not empty, hides the bug instead of fixing it.

**How to verify.** Search the domain code for `UtcNow` and `Now` outside the clock adapter, then run Example A's exact-prefix check with an instant in a past year; it fails while the bug is present.

### Task 5: Boundary evidence

Test empty identity and a fixed instant around a date boundary.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var utc = TimeSpan.Zero;
var edge = new DateTimeOffset(2024, 12, 31, 23, 59, 59, utc);
var service = new StampService(new FixedClock(edge));
string yearEnd = "2024-12-31T23:59:59.0000000+00:00:a";
Check(service.Stamp("a") == yearEnd, "year end");
var next = new StampService(new FixedClock(edge.AddSeconds(1)));
string newYear = "2025-01-01T00:00:00.0000000+00:00:a";
Check(next.Stamp("a") == newYear, "next second is next year");
var plusTwo = edge.ToOffset(TimeSpan.FromHours(2));
var local = new StampService(new FixedClock(plusTwo));
string shifted = "2025-01-01T01:59:59.0000000+02:00:a";
Check(local.Stamp("a") == shifted, "same instant, next date");
bool Rejects(string id) {
  try {
    service.Stamp(id);
    return false;
  } catch (ArgumentException) {
    return true;
  }
}
Check(Rejects("") && Rejects("   "), "blank identity rejected");
```

**Observe:** The last second of 2024 stamps as 2024-12-31, one second later is 2025-01-01, the same instant at +02:00 already reads 2025-01-01, and empty or blank identities are rejected.

A fixed clock lets the test stand exactly on the boundary. One added second crosses the year, and the same instant viewed at offset +02:00 is already on the next calendar date, so a stamp's date depends on the offset as well as the instant. The identity rule runs before the clock is read, so it rejects both the empty string and whitespace regardless of the instant.

**Plausible wrong approach.** Assuming the date part identifies the day independent of offset leads to reports that put the same event on two different days.

**How to verify.** Compare `edge == plusTwo` and confirm it is true even though the stamps differ, which shows they are the same instant.

### Task 6: Transfer and justify

Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.

A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.

A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

## Review before continuing

Run the reference and confirm it prints `csharp-040: passed`, then rerun the guide's counterexample.
