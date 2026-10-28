## Compilation is part of the execution model

Julia specializes methods for argument types and compiles executable code when needed. The first call can include inference, compilation and initialization. A later call with the same relevant types may reuse that work. The classroom starts a fresh process for every run, so pressing Run repeatedly does not create one long warm session. Compare repeated calls inside the same program when investigating steady-state cost. Startup latency remains a valid user experience metric; it simply answers a different question.

A benchmark has a workload contract: input size and types, required result, mutation policy, thread configuration and measured boundary. Let \(T_{\mathrm{total}}=T_{\mathrm{startup}}+T_{\mathrm{compile}}+T_{\mathrm{kernel}}\) denote a conceptual decomposition, not an exact accounting that a single stopwatch can identify. A wall-clock observation includes scheduling noise and other processes. A faster observed call is evidence about that trial, not a theorem about all hardware.

## Type inference makes uncertainty visible

The compiler attempts to infer what types an expression can produce. Concrete input containers and a well-chosen accumulator often let it infer one result type. `@inferred` checks agreement between the inferred return type and the observed result for a particular call. It is a useful regression assertion, but it does not prove allocation freedom, numerical correctness or speed.

Start the sum of squares at `zero(eltype(values))` for a container of concrete floating values. This expresses the additive identity in the element type. Starting with an unrelated type can introduce conversions or a type-changing loop variable. Generic code still needs an arithmetic contract: integer accumulation can overflow, and the return type of arbitrary user-defined multiplication need not match its operands.

### Worked case A: inspect a bounded kernel

The first program checks exact small values and inferred output, warms the kernel, and captures the compiler's textual report into a buffer. Read the report for unexpected uncertainty. It is diagnostic text, so the reference does not assert a particular compiler print layout.

{{WORKED_A}}

The result 55 follows from \(1^2+2^2+3^2+4^2+5^2\). The independent arithmetic expectation is stronger than checking that two versions return the same wrong value. In scientific code, protect the algorithm before tuning its implementation.

### Worked case B: report measurements without ranking noise

The second program repeats the warmed operation and reports elapsed seconds and allocated bytes. Returning the value alongside measurements preserves the result and helps detect accidental changes in the measured operation. The assertions concern outputs and valid measurement domains. They do not demand a particular number of nanoseconds.

{{WORKED_B}}

## Profiling and the next decision

A stopwatch tells you that a boundary is costly; a profiler samples or instruments where time is spent. Julia's `Profile` standard library can collect stacks, but a tiny deterministic classroom kernel may finish before useful samples accumulate. In a separate prepared project, profile a representative longer workload, inspect allocation hot spots, and repeat the same benchmark after one change. Record package and Julia versions with the input generator.

Do not optimize an unused microbenchmark while ignoring CSV parsing, model compilation, plotting or I/O in the real application. Avoid global untyped state in hot loops, but do not replace every abstraction with manual code. A function barrier separates input preparation from a specialized numerical kernel and often preserves readability. Unit 26 examines storage reuse; unit 30 introduces bounded parallel work. Neither technique guarantees improvement for small inputs.

## Mistakes and transfer

Comparing a cold call against a warm one rewards the order of measurement. Comparing different results rewards incorrect work. Suppressing bounds checks before proving valid indices can turn an ordinary exception into unsafe behavior. Retain checks while developing, use independent numerical tests, and treat an optimization claim as an experiment with a declared workload. A production report should include distributions of repeated timings and memory observations rather than one favorable minimum.
