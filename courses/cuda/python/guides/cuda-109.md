# cuda-109: Deployment runtimes and engine building

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-090`, `cuda-095`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **define the shape envelope**, **choose calibration data**, and **compare task quality** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Export translates a model into an interchange or runtime representation. Building an execution engine chooses supported implementations for target shapes, precision and hardware. Successful export is weaker evidence than successful execution, and one successful shape is weaker than a complete supported-shape contract. Calibration for selected quantization workflows must use representative data separate from evaluation.

An optional TensorRT or another prepared runtime has its own operator, platform and version constraints. Engine caches may depend on hardware, toolkit and runtime versions. Preserve the source model and build recipe, then compare outputs and task quality over a bounded shape set. Report engine build, cold start and warm inference separately. The classroom's default CPU workers do not imply an engine builder is installed.



### Key terms

- **Model export:** Translating a model into an interchange or runtime representation, which is weaker evidence than successful execution.
- **Engine build:** Selecting supported kernels for target shapes, precision and hardware to produce an executable inference engine.
- **Shape envelope:** The range of input shapes an engine was built and tested to accept.
- **Calibration data:** Representative inputs, kept separate from evaluation data, used to choose quantization ranges.

## Worked examples

### Worked example 1

A deployment accepts batch sizes 1 through 8 and sequence lengths up to 32. Batch 9 should be rejected or handled by a separately documented path rather than silently truncating input.

### Worked example 2

A lower-precision engine that passes shape checks but changes classification quality beyond tolerance fails the application contract despite compiling successfully.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def accepted(batch, sequence):
    return 1 <= batch <= 8 and 1 <= sequence <= 32


assert accepted(1, 32)
assert not accepted(9, 16)
assert not accepted(2, 0)
print("CPU deployment contract: supported shapes accepted; invalid shapes rejected")
```

**Expected observation:** Declared shape envelope enforced.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Define the shape envelope

**Trap to avoid:** Leaving the envelope implicit means unsupported shapes reach the engine and fail with internal errors or are padded and truncated without notice.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Reject an invalid request

**Trap to avoid:** Splitting batch 9 into 8 and 1 automatically may be reasonable, but only as a documented path. Doing it implicitly changes latency and behavior without a contract.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Separate export build and execution

**Trap to avoid:** Reporting the deployment as working because the export succeeded skips build and execution, where unsupported operators and precision problems usually appear.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Choose calibration data

**Trap to avoid:** Calibrating on a handful of constant inputs gives ranges that clip real activations, which lowers accuracy. Values outside the calibrated range saturate at the limit, so large activations lose their differences entirely.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Record engine compatibility

**Trap to avoid:** Copying an engine file to a different GPU model or runtime release can fail to load or behave differently. Rebuilding per target from the same exported graph is the safer pattern.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Compare task quality

**Trap to avoid:** Comparing only a few output tensors for closeness can miss a quality drop concentrated in some classes.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Define the shape envelope".
2. Change one assumption in worked example 2 while preserving the declared contract: reject an invalid request.
3. Trace the CPU program's variables before adding hardware behavior: separate export build and execution.
4. Draw producers, consumers and the exact operation boundary for the task "Choose calibration data".
5. Separate what the small fixture establishes from what the real runtime must show: record engine compatibility.
6. Write a counterexample to an overbroad claim before you compare task quality.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Define the shape envelope`. For the final claim use `Compare task quality`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-109: Deployment runtimes and engine building.
Read courses/cuda/python/guides/cuda-109.md and courses/cuda/python/lessons/cuda-109.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
