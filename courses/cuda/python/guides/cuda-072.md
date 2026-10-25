# cuda-072: Capability and failure diagnosis

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-065`, `cuda-071`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **order the evidence levels**, **design fail-closed device selection**, and **compare alternative backend labels** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Readiness is a sequence of increasingly strong claims: the package imports, the device is visible, allocation works, a compatible binary launches, execution completes, and the answer is correct. A successful earlier step cannot prove a later one. A missing device in a container may be a host/runtime exposure issue; an unsupported architecture binary is a build issue; an allocation failure may be a workload budget issue.

Fail clearly instead of silently substituting CPU execution in a GPU evidence run. A CUDA device assertion can poison later operations in that process, so the first failure and process boundary matter. Stop and report a bounded failed job rather than repeatedly retrying allocations. On unsupported hosts, use the portable reference route and keep real-device evidence pending. MPS, ROCm and other accelerator backends are alternatives with different contracts, not CUDA emulation.



## Worked examples

### Worked example 1

A probe that imports CuPy but reports no device establishes package installation only. Mark allocation and kernel tests as not attempted.

### Worked example 2

A probe that launches but returns wrong values establishes execution, then fails correctness. It must not be summarized as ready simply because the exit status was zero.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
stages = ["import", "visibility", "allocation", "launch", "completion", "correctness"]
observed = {name: True for name in stages}
observed["correctness"] = False
assert not all(observed.values())
failed = next(name for name in stages if not observed[name])
assert failed == "correctness"
print("CPU diagnostic fixture: failed at", failed)
```

**Expected observation:** Fixture fails at correctness, not readiness success.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Order the evidence levels

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **order the evidence levels** in the examples above.

### Exercise 2: Classify missing device

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **classify missing device** in the examples above.

### Exercise 3: Classify wrong output

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **classify wrong output** in the examples above.

### Exercise 4: Design fail-closed device selection

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **design fail-closed device selection** in the examples above.

### Exercise 5: Explain process restart after fatal device error

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **explain process restart after fatal device error** in the examples above.

### Exercise 6: Compare alternative backend labels

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **compare alternative backend labels** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Order the evidence levels".
2. Change one assumption in worked example 2 while preserving the declared contract: classify missing device.
3. Trace the CPU program's variables before adding hardware behavior: classify wrong output.
4. Draw producers, consumers and the exact operation boundary for the task "Design fail-closed device selection".
5. Separate what the small fixture establishes from what the real runtime must show: explain process restart after fatal device error.
6. Write a counterexample to an overbroad claim before you compare alternative backend labels.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Order the evidence levels`. For the final claim use `Compare alternative backend labels`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-072` using `courses/cuda/python/guides/cuda-072.md` and `courses/cuda/python/lessons/cuda-072.md`. Help me reason about Capability and failure diagnosis. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
