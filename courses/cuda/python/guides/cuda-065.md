# cuda-065: Which processor ran this line?

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-005`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **trace the five events**, **find the hidden transfer in scalar printing**, and **explain how a CPU fallback must be labeled** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

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

### Exercise 1: Trace the five events

**Trap to avoid:** Listing only three events (build, sum, print) merges the upload into construction and the download into printing. That hides exactly the two transfers worked example 2 names, so a later timing or residency question has no event to attach to.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Explain why import is insufficient

**Trap to avoid:** Treating a clean import as proof of GPU execution is the common shortcut. It fails on a CPU-only laptop where the import succeeds but the first allocation raises, and it fails silently when a framework falls back to CPU for unsupported work.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Change the input to an empty list

**Trap to avoid:** Launching a reduction with a grid computed from `n = 0` and then reading `out[0]` can return whatever bytes the allocation held. Another wrong move is raising an error, which breaks callers that legitimately pass empty batches.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Find the hidden transfer in scalar printing

**Trap to avoid:** Assuming `print(total)` is free because it is one line leads to placing it inside a loop. Each iteration then stalls the host until the device catches up, and a timing taken around the loop measures synchronization rather than the reduction.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design a residency ledger

**Trap to avoid:** A ledger keyed by package name ("numpy", "cupy") instead of by object fails as soon as one library holds both host and device arrays, and it cannot record whether the device result was actually ready when read.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Explain how a CPU fallback must be labeled

**Trap to avoid:** Catching the CUDA error and silently computing with NumPy makes the program exit with status zero and the same answer. A dashboard reading only exit codes would then count a GPU lesson as qualified on a machine with no GPU.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Trace the five events".
2. Change one assumption in worked example 2 while preserving the declared contract: explain why import is insufficient.
3. Trace the CPU program's variables before adding hardware behavior: change the input to an empty list.
4. Draw producers, consumers and the exact operation boundary for the task "Find the hidden transfer in scalar printing".
5. Separate what the small fixture establishes from what the real runtime must show: design a residency ledger.
6. Write a counterexample to an overbroad claim before you explain how a CPU fallback must be labeled.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Trace the five events`. For the final claim use `Explain how a CPU fallback must be labeled`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-065: Which processor ran this line?.
Read courses/cuda/python/guides/cuda-065.md and courses/cuda/python/lessons/cuda-065.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
