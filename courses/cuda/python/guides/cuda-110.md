# cuda-110: Custom operator packaging and binary portability

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-061`, `cuda-097`, `cuda-098`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **list compatibility axes**, **design a build ledger**, and **define a package release gate** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A native extension package combines Python compatibility, framework ABI, host compiler, CUDA toolkit, architecture targets and system libraries. A wheel filename alone does not promise every GPU can execute its embedded code. Native device binaries target architectures; intermediate representations can provide a JIT path only within supported compatibility rules. Record what was built and what was actually executed.

Use a fixed project with reviewed build dependencies and reproducible metadata. Test import, operator registration, forward/backward behavior and unsupported-input failure in each declared environment. Keep build-time downloads explicit and separate from classroom reading. The browser's single-file pad does not become a general package manager. Publishing packages or using external registries is a separately authorized workflow.



### Key terms

- **Framework ABI:** The binary interface of a framework build that a native extension must match.
- **Wheel:** A built Python package whose tags describe Python and platform compatibility but not every GPU it can run on.
- **Native cubin:** Compiled device code for a specific GPU architecture that runs without just-in-time compilation.
- **PTX:** An intermediate representation that the driver can JIT-compile for newer architectures within compatibility rules.
- **Build ledger:** A record of compiler, toolkit, framework, architecture targets and what was actually executed.

## Worked examples

### Worked example 1

A package can import because its host shared library loads, then fail when the first kernel lacks compatible device code. Import is only the first qualification step.

### Worked example 2

Two environments with the same Python version but different framework ABI or CUDA assumptions may need separate builds. Preserve a matrix rather than claiming universal portability.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
required = {"python", "framework", "toolkit", "host_arch", "device_targets"}
manifest = {
    "python": "pinned",
    "framework": "pinned",
    "toolkit": "pinned",
    "host_arch": "declared",
    "device_targets": ["qualified separately"],
}
assert set(manifest) == required
assert "driver" not in manifest
print("CPU package ledger: build metadata complete; runtime driver still separate")
```

**Expected observation:** Build ledger completeness does not establish runtime driver or GPU acceptance.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: List compatibility axes

**Trap to avoid:** Recording only the Python version suggests one wheel works everywhere that Python runs, while a framework ABI change alone can break the import.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Separate import and execution

**Trap to avoid:** Treating a successful import as proof of portability passes packages that cannot run any kernel on the target GPU.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Explain native code versus intermediate code

**Trap to avoid:** Shipping native code only for the build machine's GPU makes the package fail on any older or newer architecture.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design a build ledger

**Trap to avoid:** Building from a developer machine without recording flags yields an artifact nobody can reproduce or audit.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Test unsupported dtype

**Trap to avoid:** Silently casting to float32 hides precision loss and gives callers a different result from what they requested.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Define a package release gate

**Trap to avoid:** Testing one environment and declaring the whole matrix supported presents untested claims as verified.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "List compatibility axes".
2. Change one assumption in worked example 2 while preserving the declared contract: separate import and execution.
3. Trace the CPU program's variables before adding hardware behavior: explain native code versus intermediate code.
4. Draw producers, consumers and the exact operation boundary for the task "Design a build ledger".
5. Separate what the small fixture establishes from what the real runtime must show: test unsupported dtype.
6. Write a counterexample to an overbroad claim before you define a package release gate.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `List compatibility axes`. For the final claim use `Define a package release gate`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-110: Custom operator packaging and binary portability.
Read courses/cuda/python/guides/cuda-110.md and courses/cuda/python/lessons/cuda-110.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
