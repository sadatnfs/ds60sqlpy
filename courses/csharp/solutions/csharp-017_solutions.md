# csharp-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-017_solution.cs](csharp-017_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared contract:** The consumer depends on the interface rather than the concrete class. Four units cost 12 and zero units cost zero.

**Change policy without changing the consumer:** An implementation can change the pricing rule while preserving units and accepted inputs. The same consumer applies a capped or uncapped policy.

## Task answers

### Task 1: Predict and explain

Trace the interface call to the selected implementation.

**Written answer.** `IRate rate = new FlatRate(3)` stores a `FlatRate` behind an `IRate` variable. `rate.Cost(4)` is an interface call, so the runtime dispatches to `FlatRate.Cost`, which computes `checked(3 * 4)` and returns 12. `Total(rate, 0)` makes the same call with 0 units and gets 0.

**Why it is correct.** The static type `IRate` decides which members can be called, while the object created by `new` decides which method body runs. `Total` never names `FlatRate`, yet it reaches that implementation through the interface slot.

**Plausible wrong approach.** Expecting `Total` to need a `FlatRate` overload, or a cast such as `((FlatRate)rate).Cost(4)`, misses the point of the contract. The cast compiles but throws `InvalidCastException` as soon as Example B passes a `CappedRate`.

**How to verify.** Add `Check(rate.GetType() == typeof(FlatRate), "runtime type");` next to the `flat rate` check. Both pass, and swapping in `new CappedRate(3, 10)` changes the result of `rate.Cost(4)` to 10 without editing `Total`.

### Task 2: Guided modification

Add a second flat rate and keep Total unchanged.

**Written answer.** Create `IRate premium = new FlatRate(5);` and check `Total(premium, 4) == 20` beside `Total(new FlatRate(3), 4) == 12`. `Total` keeps its one-line body.

**Why it is correct.** `FlatRate` is a positional record, so each instance carries its own `Price`. `Total` reads the price only through `Cost`, so a second rate needs no change in the consumer.

**Plausible wrong approach.** Adding a `price` parameter to `Total` and computing `price * units` inside it bypasses the interface. The capped policy then disappears, because `Total(capped, 4)` would ignore `Cap` and return 12 instead of 10.

**How to verify.** Run both checks plus the existing `capped policy` check; all pass. `git diff` on the `Total` line should show no change.

### Task 3: Independent construction

Define a small interface for a deterministic label formatter.

**Written answer.** Declare `public interface ILabelFormatter { string Format(string name, int count); }` and implement `public sealed record PlainLabel : ILabelFormatter { public string Format(string name, int count) => $"{name}:{count}"; }`. The contract states that equal inputs always produce the same text.

**Why it is correct.** One method with explicit inputs keeps the interface small, and a deterministic implementation can be tested by comparing strings. Nothing in the contract depends on time, culture or random state.

**Plausible wrong approach.** An implementation using `$"{name}:{count:N0}"` looks harmless but formats 1234 as `1,234` or `1.234` depending on `CultureInfo.CurrentCulture`, so the same inputs give different labels on different machines.

**How to verify.** Check `new PlainLabel().Format("pear", 3) == "pear:3"` and that two calls with the same arguments return equal strings. Add `Format("pear", 1234) == "pear:1234"`; the `N0` variant fails it wherever the culture inserts a group separator.

### Task 4: Diagnose a defect

Diagnose an implementation returning cents where the contract requires whole currency units.

**Written answer.** A `CentsRate(300)` whose `Cost(4)` returns 1200 has the right signature but breaks the contract that results are whole currency units. `Total` passes 1200 on as if it were 1200 units of currency, a hundredfold overcharge. Convert inside the implementation or reject it.

**Why it is correct.** The compiler checks only that `Cost` takes and returns `int`. Units are part of the behavior callers rely on, so two implementations that disagree on units are not substitutable even though both compile.

**Plausible wrong approach.** Dividing by 100 inside `Total` fixes the cents implementation but breaks `FlatRate`: `Total(new FlatRate(3), 4)` becomes 0 because integer division truncates 12 / 100.

**How to verify.** Run the same consumer test against both implementations: `Total(rate, 4)` must be 12 for a price of 3 whole units. The cents version fails with 1200, and after the fix both return 12.

### Task 5: Boundary evidence

Test zero and a value exactly at the cap.

**Written answer.** For `CappedRate(3, 10)`, check `Total(rate, 0) == 0`. The cap is reached when `3 * units == 10`, which has no integer solution, so test the nearest values: 3 units cost 9 (below the cap) and 4 units cost 10 (capped). Use `CappedRate(5, 10)` to hit the cap exactly with 2 units.

**Why it is correct.** `Math.Min(Price * units, Cap)` returns the product when it is at or below the cap and the cap above it. Testing 9, exactly 10 and 12 before capping shows both branches and the equality case.

**Plausible wrong approach.** Capping the unit count instead of the cost, as in `Price * Math.Min(units, Cap / Price)`, looks equivalent but `Cap / Price` truncates 10 / 3 to 3, so `CappedRate(3, 10).Cost(4)` returns 9 and undercharges by 1. Only a test at or just past the cap shows it.

**How to verify.** Check `new CappedRate(5, 10).Cost(2) == 10`, `new CappedRate(3, 10).Cost(3) == 9` and `Total(new CappedRate(3, 10), 0) == 0`. All pass silently.

### Task 6: Transfer and justify

Choose one dependency worth injecting in the inventory importer and explain the testing benefit.

**Written answer.** Inject the source of inventory rows, for example `interface IRowSource { IEnumerable<string> ReadRows(); }`, instead of letting the importer call `File.ReadAllLines` itself. Production passes a file-backed source; tests pass an in-memory list.

**Why it is correct.** The importer's parsing and validation rules can then be tested with exact rows, including malformed ones, without creating files or depending on paths. The limitation is one more type to maintain and wire up at startup.

**Plausible wrong approach.** Injecting an interface for the importer's own private parsing helper adds indirection without a testing benefit, because tests already reach that helper through the public import call. The pitfall is an interface that exposes implementation detail.

**How to verify.** Write a test with an in-memory source containing `"pear,2"` and `"bad"`. Check that one item is imported and one row is reported as rejected, without touching the file system.

## Mechanism and diagnostic reasoning

An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.

`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.

Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

## Review before continuing

Run the reference and confirm that it prints `csharp-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
