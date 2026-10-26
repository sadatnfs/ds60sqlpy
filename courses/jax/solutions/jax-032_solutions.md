# jax-032: explained reference

The minimal numerical oracle can be \(f(x)=x^2\) on \(x=(1,2,3)\), giving (1,4,9). The equation is deliberately trivial so evidence can focus on execution identity and completion. A later performance ratio must compare completed equivalent work with shape, dtype, transfers and warmup fixed. Logical payload bytes are \(N\times\mathrm{bytes\ per\ element}\); they are not peak allocator usage.

## Exercise 1: Separate CPU evidence

The same mathematics can be correct while the accelerator toolchain or device operation remains untested.

**Expected:** It supports CPU numerical behavior only.

Retain the CPU receipt as a baseline and list the missing accelerator stages.

## Exercise 2: Separate compilation from execution

Compilation can succeed without establishing that the intended device operation completed correctly.

**Expected:** Compilation evidence, with execution/readback still missing.

The next required observation is an owned bounded execution with synchronization and an independent value check.

## Exercise 3: Choose a memory measurement

Repeated controlled measurements and ownership checks are needed to diagnose a leak; one large pool is not sufficient evidence.

**Expected:** Allocator reservation and non-array/intermediate overhead can differ from logical payload.

Report logical array payload, allocator reservation and measured peak separately, with the runtime's allocation policy.

## Exercise 4: Design a precision comparison

Accuracy and speed are distinct outcomes. Hardware-specific observations cannot be assumed from the dtype name.

**Expected:** A plan with analytic/reference values, conditioning, tolerances, actual dtype and separately synchronized timings.

Hold inputs and operation fixed; validate numerical error first; then measure completed execution under the chosen precision policy.

## Exercise 5: Distinguish TPU qualification

The GPU receipt does not establish another backend's package or hardware behavior.

**Expected:** A separately prepared TPU environment, actual TPU allocation/computation/readback and target-specific measurements.

Use the same mathematical oracle where appropriate, while retaining separate environment and device evidence.

## Exercise 6: Handle uncertain device health

The repository's optional-device workflow treats serious faults separately from an ordinary repairable syntax error and never resets a shared GPU automatically.

**Expected:** Process cleanup alone does not prove device recovery; retain the outcome for the resource owner to inspect.

Preserve the receipt, identify the owned device and require the explicit recovery workflow before requalification.

## Scope of this evidence

Hardware acceptance needs actual observations from the selected backend. No source snippet, imported package, CPU fallback or compiler artifact substitutes for allocation, synchronized computation and readback. Avoid global driver changes or device resets as incidental troubleshooting.

Prepare an optional device-study specification with ownership, bounded inputs, source identity, correctness oracle, timing boundary, memory measurements and recovery responsibility. Execute it only through an explicitly prepared compatible workflow; this reading lesson launches nothing.
