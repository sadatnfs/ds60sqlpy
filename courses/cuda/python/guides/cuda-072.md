# cuda-072: Capability and failure diagnosis

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-065`, `cuda-071`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **order the evidence levels**, **design fail-closed device selection**, and **compare alternative backend labels** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Readiness is a sequence of increasingly strong claims: the package imports, the device is visible, allocation works, a compatible binary launches, execution completes, and the answer is correct. A successful earlier step cannot prove a later one. A missing device in a container may be a host/runtime exposure issue; an unsupported architecture binary is a build issue; an allocation failure may be a workload budget issue.

Fail clearly instead of silently substituting CPU execution in a GPU evidence run. A CUDA device assertion can poison later operations in that process, so the first failure and process boundary matter. Stop and report a bounded failed job rather than repeatedly retrying allocations. On unsupported hosts, use the portable reference route and keep real-device evidence pending. MPS, ROCm and other accelerator backends are alternatives with different contracts, not CUDA emulation.



### Key terms

- **Readiness ladder:** An ordered sequence of claims from package import through device visibility, allocation, launch and a correct answer, where an earlier step cannot prove a later one.
- **Fail-closed device selection:** A policy that stops with a clear error when the requested GPU is unavailable instead of silently running on the CPU.
- **Device-side assertion:** A failure raised inside a kernel that can leave the CUDA context unusable, so later operations in the same process also fail.
- **Process boundary:** The point at which a fresh process obtains a new context after a fatal device error, since the old context cannot be recovered.

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `failed` | `'correctness'` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Order the evidence levels

**Trap to avoid:** Collapsing all stages into one boolean `gpu_ok` hides where a failure happened and makes a correctness failure look like a missing driver.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Classify missing device

**Trap to avoid:** Reinstalling CuPy treats the problem as a package issue when the package is fine; the missing piece is device exposure or hardware.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Classify wrong output

**Trap to avoid:** Reporting the probe as ready because the exit code was zero ignores the value check. A probe that prints wrong numbers and exits normally is worse than one that crashes, because nothing downstream notices.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design fail-closed device selection

**Trap to avoid:** Defaulting to CPU with a warning lets automated runs record a GPU pass for a CPU result.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Explain process restart after fatal device error

**Trap to avoid:** Catching the exception and retrying in the same process often fails again, and if it seems to succeed the evidence is suspect.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Compare alternative backend labels

**Trap to avoid:** Calling any accelerator run a GPU pass loses which runtime produced it, so a CUDA requirement can be satisfied by an Apple run on paper.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

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

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-072: Capability and failure diagnosis.
Read courses/cuda/python/guides/cuda-072.md and courses/cuda/python/lessons/cuda-072.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
