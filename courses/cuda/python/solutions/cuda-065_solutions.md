# cuda-065: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace the five events

Construction and retrieval belong to the host.

**Approach.** Walk the GPU sum in time order and tag each step with the processor that does it: the Python list is built by the interpreter, a copy moves those three integers into a device allocation, a reduction kernel runs on the GPU, a completion point is reached, and a scalar copy brings the total back.

**Why it is correct here.** Only the launch and the arithmetic run on the device. The interpreter creates `[1, 2, 3]` before any driver call, and the final `6` must be copied into host memory before Python can treat it as an `int`, so the first and last events belong to the host.

**A plausible wrong approach.** Listing only three events (build, sum, print) merges the upload into construction and the download into printing. That hides exactly the two transfers worked example 2 names, so a later timing or residency question has no event to attach to.

**How to verify.** Write the five events in a table with a processor column and compare it with worked example 2. Then run `courses/cuda/python/references/cuda-065_cpu.py` and confirm its ledger reports CPU for every row, which is the honest result when no device participates.

## Exercise 2: Explain why import is insufficient

Import proves only Python resolution.

**Approach.** Separate what `import cupy` establishes from what a GPU result requires: a package resolved on `sys.path`, then a visible device, an allocation, a launch, completion and a correct value. Each later fact needs its own observation.

**Why it is correct here.** Python import only loads modules and may defer driver initialization. A machine without an NVIDIA driver can still import a wheel successfully, so the import line in this chapter says nothing about where the later `sum` executes.

**A plausible wrong approach.** Treating a clean import as proof of GPU execution is the common shortcut. It fails on a CPU-only laptop where the import succeeds but the first allocation raises, and it fails silently when a framework falls back to CPU for unsupported work.

**How to verify.** On any host, note that import succeeded, then try a one-element device allocation and record the outcome separately. The reasoning is correct if your notes contain two distinct lines, one for import and one for allocation, rather than a single ready flag.

## Exercise 3: Change the input to an empty list

The additive identity is zero.

**Approach.** Replace `[1, 2, 3]` with `[]` and ask what the reduction must return. A sum of no terms is the additive identity, so the result is `0`, and on a GPU path the sensible move is to return that identity without launching anything.

**Why it is correct here.** `sum([])` in Python returns `0` by definition, and the reference asserts exactly that. A device reduction with zero elements has no work, so any correct backend must agree with the host identity rather than read uninitialized storage.

**A plausible wrong approach.** Launching a reduction with a grid computed from `n = 0` and then reading `out[0]` can return whatever bytes the allocation held. Another wrong move is raising an error, which breaks callers that legitimately pass empty batches.

**How to verify.** Run the reference and confirm the line `assert sum([]) == 0` passes. For a GPU variant, test the empty input explicitly and check that the returned value is `0` and that no kernel launch was recorded.

## Exercise 4: Find the hidden transfer in scalar printing

Scalar materialization transfers and may synchronize.

**Approach.** Look for the point where a device value becomes a Python object. Calling `print`, `float()`, `int()` or `.item()` on a device scalar requests its value on the host, which needs a device-to-host copy and therefore waits for the kernel that produces it.

**Why it is correct here.** In worked example 2 the reduction result lives in device memory. Python cannot format bytes it does not hold, so printing forces the copy and the copy cannot begin until the producing kernel completes, which adds a synchronization the code never states.

**A plausible wrong approach.** Assuming `print(total)` is free because it is one line leads to placing it inside a loop. Each iteration then stalls the host until the device catches up, and a timing taken around the loop measures synchronization rather than the reduction.

**How to verify.** Mark the print as event five in your trace and label it as both a transfer and a wait. On a real device, a profiler timeline would show a small device-to-host copy right before the host resumes; without a device, the trace table is the evidence.

## Exercise 5: Design a residency ledger

Record object, backend, allocation and completion.

**Approach.** Design a ledger row per object with four fields: the object name, the backend that owns it, the allocation that holds its bytes, and the event that proves it is complete. Fill it for input, sum and result.

**Why it is correct here.** The reference ledger `[("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]` records only the backend. Adding allocation and completion columns is what lets the same ledger describe the GPU path, where input and result have two copies each.

**A plausible wrong approach.** A ledger keyed by package name ("numpy", "cupy") instead of by object fails as soon as one library holds both host and device arrays, and it cannot record whether the device result was actually ready when read.

**How to verify.** Fill the ledger for the CPU case and check that every row says CPU, matching the reference assertion `all(device == "CPU" ...)`. Then fill it for the five-event GPU trace and confirm the input and result each have a host row and a device row.

## Exercise 6: Explain how a CPU fallback must be labeled

Report CPU reference rather than GPU success.

**Approach.** When a GPU path is unavailable and the program computes on the CPU instead, report it as a CPU reference result with the reason, for example "CPU reference: 6; device not visible", and never as a GPU pass.

**Why it is correct here.** The reference in this chapter prints `CPU reference: 6` and every ledger entry is CPU. That value is mathematically right, but it is evidence that the algorithm is correct, not that any CUDA device executed it.

**A plausible wrong approach.** Catching the CUDA error and silently computing with NumPy makes the program exit with status zero and the same answer. A dashboard reading only exit codes would then count a GPU lesson as qualified on a machine with no GPU.

**How to verify.** Run the reference on a CPU-only host and confirm the printed label starts with `CPU reference`. A correct fallback report contains the backend name, the reason, and the value, and a reviewer can see that the GPU stage was not attempted.

## Reference observation

CPU reference: 6; every ledger event is CPU.

The reference file is `courses/cuda/python/references/cuda-065_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
