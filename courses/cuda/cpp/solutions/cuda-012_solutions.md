# cuda-012: explanatory solutions

## Mechanism review

The `__global__` qualifier declares a kernel callable through CUDA launch syntax. In `fill<<<blocks, threads>>>(out,n)`, the angle-bracket configuration chooses a grid of blocks and threads per block; parentheses carry ordinary function arguments. Each thread reads its own indices to choose work. A launch normally submits work asynchronously. Checking cudaGetLastError after submission detects launch problems, while a checked synchronization or dependent copy exposes execution failures. Only after the dependency is complete should the host validate returned values. Device printf is a debugging tool with ordering and buffering limitations, not a replacement for checking the output buffer.

The separate [CPU reference](../references/cuda-012_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Let one kernel write its global index into a five-element output using eight launched threads. Threads 0 through 4 write \([0,1,2,3,4]\); threads 5 through 7 perform no write because the bounds predicate is false. The host compares every returned value with its expected index.

## Exercise 2

Change the expression to twice the index plus one. Expected output is \([1,3,5,7,9]\). Keeping the same ownership mapping separates the arithmetic change from scheduling. A launch status of success without a completion check does not establish these values arrived in host memory.

## Exercise 3

Two blocks with 32 threads each are launched, and out plus count 50 are kernel arguments. Fourteen thread positions must avoid writing.

## Exercise 4

Checked completion, transfer of output and host validation. Successful submission alone does not establish a finished kernel.

## Exercise 5

Use a host early return or another explicitly valid empty-work policy; do not launch a grid with zero blocks.

## Exercise 6

State the actual device, count and validated result contract after completion. Avoid claiming performance or general correctness from five values.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-012_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State the actual device, count and validated result contract after completion. Avoid claiming performance or general correctness from five values.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
