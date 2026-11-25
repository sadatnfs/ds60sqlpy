# cuda-072: Capability and failure diagnosis

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-003`, `cuda-065`, `cuda-071`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Order the evidence levels.
- Classify missing device.
- Classify wrong output.
- Design fail-closed device selection.
- Explain process restart after fatal device error.
- Compare alternative backend labels.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-072_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-072_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-072.md) before opening hints.

### Exercise 1: Order the evidence levels

**Trap to avoid:** Collapsing all stages into one boolean `gpu_ok` hides where a failure happened and makes a correctness failure look like a missing driver.

### Exercise 2: Classify missing device

**Trap to avoid:** Reinstalling CuPy treats the problem as a package issue when the package is fine; the missing piece is device exposure or hardware.

### Exercise 3: Classify wrong output

**Trap to avoid:** Reporting the probe as ready because the exit code was zero ignores the value check. A probe that prints wrong numbers and exits normally is worse than one that crashes, because nothing downstream notices.

### Exercise 4: Design fail-closed device selection

**Trap to avoid:** Defaulting to CPU with a warning lets automated runs record a GPU pass for a CPU result.

### Exercise 5: Explain process restart after fatal device error

**Trap to avoid:** Catching the exception and retrying in the same process often fails again, and if it seems to succeed the evidence is suspect.

### Exercise 6: Compare alternative backend labels

**Trap to avoid:** Calling any accelerator run a GPU pass loses which runtime produced it, so a CUDA requirement can be satisfied by an Apple run on paper.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Arrange the claims from weakest to strongest, asking for each what a success at that step still leaves unproven.
2. Decide whether a missing device is a property of the package, the container runtime or the host, and what you would inspect first.
3. The program launched and finished. Which claim in the ladder failed when the values came back wrong?
4. Write the selection rule so that a missing requested backend ends the run with a clear error instead of switching processors.
5. Ask whether operations queued after a device assertion in the same process can still be trusted.
6. For each backend name, state what hardware and software it implies, then check that the label matches what actually ran.

## Common mistakes and self-check

A frequent mistake is summarizing a probe as ready because its exit status was zero. In worked example 2 the kernel launched and completed but returned wrong values, which is a correctness failure. Another is letting a GPU evidence run quietly fall back to CPU when no device is visible. Fix both by recording each evidence level separately, failing closed when the requested backend is absent, and restarting the process after a fatal device error.

**Evidence limit:** The fixture stops at the correctness level on purpose and never touches real hardware. It teaches how to classify failures; it does not diagnose your driver, container runtime exposure or binary architecture, which need checks on the actual host.

1. Why can a successful import not prove a device is usable?
2. How do you classify an unsupported architecture binary versus an allocation failure?
3. Is MPS or ROCm a way to emulate CUDA?

Answers: [self-check answers](../solutions/cuda-072_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-072: Capability and failure diagnosis.
Read courses/cuda/python/guides/cuda-072.md and courses/cuda/python/lessons/cuda-072.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
