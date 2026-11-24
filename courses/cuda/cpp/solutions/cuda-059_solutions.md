# cuda-059: explanatory solutions

## Mechanism review

PTX is a virtual instruction language, while SASS describes machine instructions for a particular GPU architecture. The driver or toolchain can translate PTX differently across targets and versions. A fat binary can contain native device images and PTX fallback according to a deliberate policy. JIT can introduce cold-start cost and compatibility constraints. Inspect compiler resource reports and generated code to test a hypothesis, such as unexpected local-memory traffic, before attempting inline assembly. Counting PTX instructions does not directly count executed hardware operations or predict runtime.

The separate [CPU reference](../references/cuda-059_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A high-level multiply-plus-add may become a fused instruction depending on types, options and target. If generated code changes, retain the numerical test because one rounding differs from two. A shorter instruction sequence is useful evidence only in combination with the workload's actual behavior.

**Approach:** Inspect generated code to see whether multiply and add became one fused instruction, and keep the numerical test either way.

**Why it is correct:** A fused multiply-add rounds once instead of twice, so results can differ slightly from separate operations.

**A plausible wrong approach:** Accepting a shorter instruction sequence as automatically better skips checking that its rounding still meets the tolerance.

**How to verify:** Compare outputs from fused and unfused builds against a high-precision reference within a stated tolerance.

## Exercise 2

A per-thread array causes reported local-memory traffic. Reducing its live range may remove spills, but it can also add recomputation. Compare the compiler report, output and uninstrumented timing under the same target. Do not edit assembly until the source-level cause is understood.

**Approach:** Read the compiler's local-memory report, shorten the array's live range, and rebuild for the same target.

**Why it is correct:** Fewer live values can remove spills, though recomputation may add instructions.

**A plausible wrong approach:** Hand-editing SASS to remove spills makes code that cannot be rebuilt or maintained.

**How to verify:** Compare the spill report, outputs and uninstrumented timings before and after.

## Exercise 3

A native image targets a hardware family; PTX requires a driver/toolchain path able to understand and compile that virtual version for the device.

**Approach:** Separate native cubin compatibility with a hardware family from PTX that the driver JIT-compiles.

**Why it is correct:** A cubin runs only on matching hardware, while PTX needs a driver that understands its virtual version.

**A plausible wrong approach:** Assuming any PTX runs on any driver ignores version requirements.

**How to verify:** Check the embedded targets with cuobjdump and the installed driver version.

## Exercise 4

Translation, instruction latency, memory behavior, parallel scheduling and repeated execution all intervene.

**Approach:** Measure time directly rather than counting PTX instructions.

**Why it is correct:** Translation to SASS, latency, memory stalls and scheduling all change real cost.

**A plausible wrong approach:** Ranking kernels by PTX length can pick a slower kernel with more memory stalls.

**How to verify:** Time both kernels under the same conditions and compare.

## Exercise 5

Revisit the supported architecture policy and toolchain, preserving a valid fallback; do not guess an architecture flag until the error disappears.

**Approach:** Revisit the supported architecture list and toolchain, and keep a fallback.

**Why it is correct:** The diagnostic means the target is not supported by this build.

**A plausible wrong approach:** Trying architecture flags until the error disappears can produce code for the wrong device.

**How to verify:** Rebuild with the documented targets and confirm the probe kernel runs.

## Exercise 6

Measure first load/JIT separately from warmed execution with source/target/driver identities and unchanged correctness fixtures.

**Approach:** Time the first load including JIT separately from later warmed runs, recording source, target and driver.

**Why it is correct:** Cold start includes compilation and module loading that warmed runs skip.

**A plausible wrong approach:** Averaging the first run with later runs hides the startup cost.

**How to verify:** Run fresh processes repeatedly and compare first-run times.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-059_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Measure first load/JIT separately from warmed execution with source/target/driver identities and unchanged correctness fixtures.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
