# cuda-012: explanatory solutions

## Mechanism review

The `__global__` qualifier declares a kernel callable through CUDA launch syntax. In `fill<<<blocks, threads>>>(out,n)`, the angle-bracket configuration chooses a grid of blocks and threads per block; parentheses carry ordinary function arguments. Each thread reads its own indices to choose work. A launch normally submits work asynchronously. Checking cudaGetLastError after submission detects launch problems, while a checked synchronization or dependent copy exposes execution failures. Only after the dependency is complete should the host validate returned values. Device printf is a debugging tool with ordering and buffering limitations, not a replacement for checking the output buffer.

The separate [CPU reference](../references/cuda-012_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Let one kernel write its global index into a five-element output using eight launched threads. Threads 0 through 4 write \([0,1,2,3,4]\); threads 5 through 7 perform no write because the bounds predicate is false. The host compares every returned value with its expected index.

**Approach:** Launch eight threads for five outputs and guard each write with i < 5.

**Why it is correct:** The predicate rejects threads 5 to 7, so each valid index is written once and nothing beyond.

**A plausible wrong approach:** Omitting the guard lets threads 5 to 7 write past the five-element allocation.

**How to verify:** Compare the returned [0, 1, 2, 3, 4] element by element after a checked synchronization.

## Exercise 2

Change the expression to twice the index plus one. Expected output is \([1,3,5,7,9]\). Keeping the same ownership mapping separates the arithmetic change from scheduling. A launch status of success without a completion check does not establish these values arrived in host memory.

**Approach:** Keep the same index mapping and change only the stored expression to 2 * i + 1.

**Why it is correct:** Ownership is unchanged, so any wrong value isolates an arithmetic error rather than scheduling.

**A plausible wrong approach:** Trusting the launch status as proof of results ignores that launches return before execution finishes.

**How to verify:** The reference asserts out == [1, 3, 5, 7, 9] and prints GPU_execution not performed.

## Exercise 3

Two blocks with 32 threads each are launched, and out plus count 50 are kernel arguments. Fourteen thread positions must avoid writing.

**Approach:** Read the triple chevrons as grid size 2 and block size 32, then count 64 threads against count 50.

**Why it is correct:** Sixty-four launched threads exceed fifty elements, so 14 threads must take the false branch.

**A plausible wrong approach:** Reading <<<2, 32>>> as 32 blocks of 2 threads reverses the configuration order.

**How to verify:** Compute 2 * 32 - 50 == 14 and confirm the kernel guard uses the count argument.

## Exercise 4

Checked completion, transfer of output and host validation. Successful submission alone does not establish a finished kernel.

**Approach:** Add a checked synchronize, copy the output back and compare it with the host reference.

**Why it is correct:** Kernel launches are asynchronous, so process exit can occur before the kernel finishes.

**A plausible wrong approach:** Checking only cudaGetLastError after launch catches configuration errors but not execution faults.

**How to verify:** Synchronize, check its status, then validate every returned value.

## Exercise 5

Use a host early return or another explicitly valid empty-work policy; do not launch a grid with zero blocks.

**Approach:** Return early on the host when count is zero, before computing a grid.

**Why it is correct:** No outputs exist, so skipping the launch is correct and avoids an invalid configuration.

**A plausible wrong approach:** Launching ceil(0 / 32) = 0 blocks yields an invalid configuration error, not a quiet no-op.

**How to verify:** Call the wrapper with count zero and assert no launch occurs and no error is reported.

## Exercise 6

State the actual device, count and validated result contract after completion. Avoid claiming performance or general correctness from five values.

**Approach:** Print device name, count and the validated property, all after completion.

**Why it is correct:** A message tied to observations lets a reader know exactly what was checked.

**A plausible wrong approach:** Printing 'GPU kernel is fast and correct' generalizes from five values and no timing.

**How to verify:** Confirm the message is emitted only on the path that passed validation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-012_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State the actual device, count and validated result contract after completion. Avoid claiming performance or general correctness from five values.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
