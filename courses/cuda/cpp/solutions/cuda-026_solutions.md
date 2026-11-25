# cuda-026: explanatory solutions

## Mechanism review

Compute Sanitizer provides several checks with different scopes. Memcheck investigates invalid and misaligned memory accesses; racecheck investigates shared-memory hazards; initcheck investigates uninitialized global-memory reads; synccheck investigates invalid synchronization use. Their observations complement mathematical tests. Instrumentation can be expensive and can change timing, so sanitizer runs are not performance samples. An automated command should select a nonzero error-exitcode, because a tool diagnostic must make the check fail even if the application itself returns success. Never conclude that one clean run proves race freedom for every input or validates unsupported global protocols.

## Exercise 1

For an array of four elements, valid indices are 0 through 3. A kernel that accesses index four has an off-by-one defect even if the returned allocation happens to contain readable bytes nearby. Memcheck is an appropriate additional diagnostic, while a CPU bounds model pinpoints the invalid logical access without a GPU.

**Approach:** Audit indices 0 through 4 against n = 4 on the CPU and run memcheck on the GPU build.

**Why it is correct:** Index 4 is outside the array whether or not nearby bytes happen to be readable.

**A plausible wrong approach:** Treating a run that did not crash as proof of safety ignores that the slack after the allocation absorbed the bad read.

**How to verify:** The reference asserts invalid == [4]; memcheck should report the access at index 4 on a GPU.

## Exercise 2

A consumer reads shared tile\([2]\) before its producer writes. Racecheck can add evidence about that hazard. Replacing the missing barrier with a host sleep does not establish an ordering relationship between those threads. Repair the dependency and still validate returned numerical values.

**Approach:** Restore the barrier between producer and consumer and use racecheck as supporting evidence.

**Why it is correct:** Only a barrier orders the store to tile[2] before the load by another thread.

**A plausible wrong approach:** A host sleep happens outside the kernel and creates no ordering between device threads.

**How to verify:** Run racecheck after the fix and also compare outputs to the CPU reference.

## Exercise 3

Initcheck addresses that class; retain ordinary result checks because initialization alone does not prove the formula is correct.

**Approach:** Choose initcheck for reads of global memory that were never written.

**Why it is correct:** Initcheck tracks whether device memory was initialized before it is read.

**A plausible wrong approach:** Memcheck alone accepts reads inside a valid allocation even if they were never written.

**How to verify:** Keep result comparisons too, since initialized but miscomputed values still pass initcheck.

## Exercise 4

It makes detected tool errors visible to automation through a nonzero status rather than relying on manual log inspection.

**Approach:** Pass --error-exitcode 99 so a detected error changes the process exit status.

**Why it is correct:** CI reads exit status, and without the flag a sanitizer can report errors and still exit zero.

**A plausible wrong approach:** Searching logs by hand for error text misses reports when log formats change.

**How to verify:** Run a known-bad fixture and confirm the job fails with status 99.

## Exercise 5

No. A ragged tail changes participating accesses and possibly synchronization. Include both sizes and additional relevant boundaries.

**Approach:** Test n = 32 and n = 33 and other boundaries under the checker.

**Why it is correct:** n = 33 adds a tail lane in a new warp and block, so accesses and barrier paths differ.

**A plausible wrong approach:** Assuming a clean full-warp run covers every size skips exactly the guards most likely to be wrong.

**How to verify:** Include both sizes in the sanitizer job and confirm both report zero errors.

## Exercise 6

Confirm the intended failing fixture diagnoses the old problem, run the corrected checker, validate normal/tail outputs and benchmark separately without instrumentation.

**Approach:** Reproduce the old failure, apply the fix, run racecheck and synccheck, validate outputs, then benchmark without tools.

**Why it is correct:** This sequence shows the fixture detects the bug, the fix removes it, and results are correct.

**A plausible wrong approach:** Benchmarking under the sanitizer reports instrumented timings that do not reflect the real kernel.

**How to verify:** Keep the failing fixture as a regression test and check it fails on the old commit.

## Self-check answers

1. **Which checker targets shared-memory hazards?** Racecheck.
2. **Why are sanitizer runs not performance evidence?** Instrumentation slows execution and changes timing.
3. **Why is a host sleep not a repair for a missing barrier?** It creates no ordering between device threads, so the race remains.

## Numerical reference and its limits

The [CPU reference](../references/cuda-026_cpu.py) reproduces worked example 1 and prints `{'CPU_bounds_audit': [4], 'tool_selection': {'out_of_bounds': 'memcheck', 'shared_hazard': 'racecheck', 'uninitialized': 'initcheck', 'invalid_barrier': 'synccheck'}}`.

## Transfer review

Confirm the intended failing fixture diagnoses the old problem, run the corrected checker, validate normal/tail outputs and benchmark separately without instrumentation.
