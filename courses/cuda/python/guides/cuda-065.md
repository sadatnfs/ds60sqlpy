# cuda-065: Which processor ran this line?

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-005`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **trace the five events**, **find the hidden transfer in scalar printing**, and **explain how a CPU fallback must be labeled** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Python is a host language in this lesson: its interpreter evaluates names, calls library functions and schedules work. A NumPy array owns CPU-accessible storage. A CuPy array normally owns device storage while its Python object keeps shape, dtype and ownership information on the host. The statement that creates a result may return before its GPU kernel completes. Printing a scalar can force a transfer and a wait, so observation can change the schedule you are observing.

Use four separate questions: which process issued the operation, which allocation contains its inputs, which processor executes the arithmetic, and which event proves the output is ready. A package import answers none of the last three. A GPU-enabled framework can also place unsupported or deliberately selected work on the CPU. Record actual tensor residency and synchronization instead of inferring placement from the package name.



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

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **trace the five events** in the examples above.

### Exercise 2: Explain why import is insufficient

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **explain why import is insufficient** in the examples above.

### Exercise 3: Change the input to an empty list

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **change the input to an empty list** in the examples above.

### Exercise 4: Find the hidden transfer in scalar printing

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **find the hidden transfer in scalar printing** in the examples above.

### Exercise 5: Design a residency ledger

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a residency ledger** in the examples above.

### Exercise 6: Explain how a CPU fallback must be labeled

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain how a CPU fallback must be labeled** in the examples above.

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

## Ask an AI tutor about this lesson

> I am studying `cuda-065` using `courses/cuda/python/guides/cuda-065.md` and `courses/cuda/python/lessons/cuda-065.md`. Help me reason about Which processor ran this line?. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
