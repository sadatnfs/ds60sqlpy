# jax-032: explained reference

The minimal numerical oracle can be \(f(x)=x^2\) on \(x=(1,2,3)\), giving (1,4,9). The equation is deliberately trivial so evidence can focus on execution identity and completion. A later performance ratio must compare completed equivalent work with shape, dtype, transfers and warmup fixed. Logical payload bytes are \(N\times\mathrm{bytes\ per\ element}\); they are not peak allocator usage.

## Solution approach

Sort each observation into the evidence layer it actually reaches: CPU numerical behavior, accelerator compilation, device execution with readback, memory accounting, precision, and device health. For every scenario, name what the observation supports, name the next observation still missing, and refuse to promote a lower layer into a claim about a higher one.

**Why it is correct here:** A CPU pass shows the mathematics, not the accelerator toolchain. A lowered program shows compilation, while execution needs synchronized output checked against an independent value. Reserved memory includes allocator pools, so it can exceed `nbytes` without a leak. A GPU probe says nothing about a TPU, and a reaped child process does not prove the device recovered.

## Exercise 1: Separate CPU evidence

The same mathematics can be correct while the accelerator toolchain or device operation remains untested.

**Expected:** It supports CPU numerical behavior only.

Retain the CPU test record as a baseline and list the missing accelerator stages.

**Plausible wrong approach:** Marking the GPU lesson qualified because every CPU assertion passed skips the accelerator package, driver and device stages entirely. The CPU record is a baseline, not a substitute.

## Exercise 2: Separate compilation from execution

Compilation can succeed without establishing that the intended device operation completed correctly.

**Expected:** Compilation evidence, with execution/readback still missing.

The next required observation is an owned bounded execution with synchronization and an independent value check.

**Plausible wrong approach:** Reporting a successful lowering as a working GPU path omits execution. A program can compile and still fail or return wrong values when it actually runs on the device.

## Exercise 3: Choose a memory measurement

Repeated controlled measurements and ownership checks are needed to diagnose a leak; one large pool is not sufficient evidence.

**Expected:** Allocator reservation and non-array/intermediate overhead can differ from logical payload.

Report logical array payload, allocator reservation and measured peak separately, with the runtime's allocation policy.

**Plausible wrong approach:** Calling reserved memory far above array `nbytes` a leak ignores preallocation by the allocator and temporary buffers. A leak claim needs repeated controlled measurements that keep growing.

## Exercise 4: Design a precision comparison

Accuracy and speed are distinct outcomes. Hardware-specific observations cannot be assumed from the dtype name.

**Expected:** A plan with analytic/reference values, conditioning, tolerances, actual dtype and separately synchronized timings.

Hold inputs and operation fixed; validate numerical error first; then measure completed execution under the chosen precision policy.

**Plausible wrong approach:** Timing float32 against float64 before checking their errors mixes two outcomes. A faster precision that loses the answer on an ill-conditioned input has not won the comparison.

## Exercise 5: Distinguish TPU qualification

The GPU test record does not establish another backend's package or hardware behavior.

**Expected:** A separately prepared TPU environment, actual TPU allocation/computation/readback and target-specific measurements.

Use the same mathematical oracle where appropriate, while retaining separate environment and device evidence.

**Plausible wrong approach:** Extending a GPU success to TPU because both are accelerators reuses evidence across backends. TPU needs its own environment, allocation, computation and readback observations.

## Exercise 6: Handle uncertain device health

The repository's optional-device workflow treats serious faults separately from an ordinary repairable syntax error and never resets a shared GPU automatically.

**Expected:** Process cleanup alone does not prove device recovery; retain the outcome for the resource owner to inspect.

Preserve the interrupted run record, identify the owned device and require the explicit recovery workflow before requalification.

**Plausible wrong approach:** Starting a new device job automatically after reaping an interrupted one assumes the hardware is healthy. Process cleanup and device recovery are separate facts for the resource owner.

## How to verify

Write a one-line ledger for each of the six scenarios with three columns: observation, supported claim, and next missing observation. Check that no row's claim mentions a layer its observation did not reach, and that the device health row ends with an explicit owner decision rather than an automatic retry.

## Scope of this evidence

Hardware acceptance needs actual observations from the selected backend. No source snippet, imported package, CPU fallback or compiler artifact substitutes for allocation, synchronized computation and readback. Avoid global driver changes or device resets as incidental troubleshooting.

Prepare an optional device-study specification with ownership, bounded inputs, source identity, correctness oracle, timing boundary, memory measurements and recovery responsibility. Execute it only through an explicitly prepared compatible workflow; this reading lesson launches nothing.
