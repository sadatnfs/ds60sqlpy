# cuda-065: Which processor ran this line?

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-005`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Trace the five events.
- Explain why import is insufficient.
- Change the input to an empty list.
- Find the hidden transfer in scalar printing.
- Design a residency ledger.
- Explain how a CPU fallback must be labeled.

## Mechanism and vocabulary

Python is a host language in this lesson: its interpreter evaluates names, calls library functions and schedules work. A NumPy array owns CPU-accessible storage. A CuPy array normally owns device storage while its Python object keeps shape, dtype and ownership information on the host. The statement that creates a result may return before its GPU kernel completes. Printing a scalar can force a transfer and a wait, so observation can change the schedule you are observing.

Use four separate questions: which process issued the operation, which allocation contains its inputs, which processor executes the arithmetic, and which event proves the output is ready. A package import answers none of the last three. A GPU-enabled framework can also place unsupported or deliberately selected work on the CPU. Record actual tensor residency and synchronization instead of inferring placement from the package name.



### Key terms

- **Host memory:** Memory attached to the CPU, where ordinary Python objects and NumPy arrays live.
- **Device memory:** Memory on the GPU board that kernels read and write; data must be allocated or copied there before a kernel can use it.
- **Asynchronous launch:** A kernel or copy request that returns control to Python before the GPU finishes the work.
- **Implicit synchronization:** A host wait triggered by an operation such as printing a scalar or converting to a host value, which blocks until queued device work completes.

## Worked examples

### Worked example 1

A CPU list [1, 2, 3] is reduced by the Python process to 6. No driver, GPU allocation or kernel is involved. The host result is immediately available after sum returns.

### Worked example 2

For a GPU sum, identify host construction, host-to-device copy, reduction launch, completion and device-to-host scalar retrieval as five events. A returned device scalar is not yet a host integer.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-065_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-065_cpu.py
```

```python
values = [1, 2, 3]
result = sum(values)
assert result == 6
assert sum([]) == 0
ledger = [("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]
assert all(device == "CPU" for _, device in ledger)
print("CPU reference:", result, ledger)
```

**Expected observation:** CPU reference: 6; every ledger event is CPU.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[1, 2, 3]` |
| `result` | `6` |
| `ledger` | `[('input', 'CPU'), ('sum', 'CPU'), ('result', 'CPU')]` |

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.asarray([1.0, 2.0, 3.0], dtype=cp.float32)
y = cp.sum(x)
cp.cuda.get_current_stream().synchronize()
assert float(y.get()) == 6.0
print("CUDA array sum:", float(y.get()), "device", x.device.id)
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-065.md) before opening hints.

### Exercise 1: Trace the five events

**Trap to avoid:** Listing only three events (build, sum, print) merges the upload into construction and the download into printing. That hides exactly the two transfers worked example 2 names, so a later timing or residency question has no event to attach to.

### Exercise 2: Explain why import is insufficient

**Trap to avoid:** Treating a clean import as proof of GPU execution is the common shortcut. It fails on a CPU-only laptop where the import succeeds but the first allocation raises, and it fails silently when a framework falls back to CPU for unsupported work.

### Exercise 3: Change the input to an empty list

**Trap to avoid:** Launching a reduction with a grid computed from `n = 0` and then reading `out[0]` can return whatever bytes the allocation held. Another wrong move is raising an error, which breaks callers that legitimately pass empty batches.

### Exercise 4: Find the hidden transfer in scalar printing

**Trap to avoid:** Assuming `print(total)` is free because it is one line leads to placing it inside a loop. Each iteration then stalls the host until the device catches up, and a timing taken around the loop measures synchronization rather than the reduction.

### Exercise 5: Design a residency ledger

**Trap to avoid:** A ledger keyed by package name ("numpy", "cupy") instead of by object fails as soon as one library holds both host and device arrays, and it cannot record whether the device result was actually ready when read.

### Exercise 6: Explain how a CPU fallback must be labeled

**Trap to avoid:** Catching the CUDA error and silently computing with NumPy makes the program exit with status zero and the same answer. A dashboard reading only exit codes would then count a GPU lesson as qualified on a machine with no GPU.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List each step of worked example 2 in order and ask, for each one, whose memory holds the value at that moment.
2. Picture a laptop with no NVIDIA driver. What does a successful import line still let you conclude there?
3. Ask what `sum` must return when nothing is added, then ask whether a zero-element launch could change that value.
4. The printed digits must exist in host memory first. Which copy puts them there, and what must finish before it starts?
5. Start from the reference ledger's three rows and add the columns a GPU run would need to tell two copies apart.
6. Read the line the reference actually prints and decide which backend that sentence names.

## Common mistakes and self-check

The common mistake is reading a successful `import cupy`, or a GPU package in the environment, as proof that the arithmetic ran on a device. In this chapter the reference sums `[1, 2, 3]` entirely in the Python process. To fix the claim, record four facts per operation: the issuing process, the allocation holding the inputs, the processor running the arithmetic and the event that proves the result is ready. Leave a column blank rather than guess.

**Evidence limit:** The reference prints `CPU reference: 6` with every ledger row on the CPU. That shows the arithmetic and the ledger format are right; it shows nothing about device residency, transfer cost or kernel completion on any GPU.

1. Why can a statement that creates a CuPy result return before the answer exists?
2. Which events in the five-event GPU sum belong to the host?
3. Why can printing a device scalar change what you were trying to observe?

Answers: [self-check answers](../solutions/cuda-065_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-065: Which processor ran this line?.
Read courses/cuda/python/guides/cuda-065.md and courses/cuda/python/lessons/cuda-065.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
