# csharp-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-040_solution.cs](csharp-040_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Inject a deterministic clock:** The domain behavior does not depend on the machine clock during the test. The result uses the supplied instant.

**Preserve a core validation rule:** Dependency variation should not weaken the invariant owned by the domain. A different clock does not bypass identity validation.

## Reason through the six tasks

1. **Predict and explain.** Identify policy and mechanism in the service.

2. **Guided modification.** Supply a second fixed clock and predict the changed timestamp.

3. **Independent construction.** Extract the inventory aggregation into a transport-independent core.

4. **Diagnose a defect.** Diagnose a domain method reading the system clock internally despite accepting a clock.

5. **Boundary evidence.** Test empty identity and a fixed instant around a date boundary.

6. **Transfer and justify.** Draw dependency direction for a command-line adapter, HTTP adapter and shared domain library.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Domain logic expresses the rules that make an operation valid. Transport and storage adapters translate external representations into those rules. If the domain directly opens a database or reads environment variables, its behavior becomes difficult to reproduce. Dependency direction should let outer adapters depend on the core contract while the core remains independent of a specific transport.

Dependency injection is a construction technique, not a requirement to install a container library. Explicit constructors are often enough. Supply clocks, identifiers and repositories where variation matters. Avoid an interface for every trivial value; use abstraction where it separates policy from an unstable or expensive mechanism.

A service constructor accepts an interface. A small in-memory implementation supports deterministic tests. A clock abstraction returns a fixed instant in tests while a real adapter would obtain current time.

A dependency container can conceal construction errors if overused. Do not inject mutable global services merely to rename global state. Keep core invariants in the core rather than duplicating them in every adapter.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
