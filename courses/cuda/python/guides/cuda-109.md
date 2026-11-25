# cuda-109: Deployment runtimes and engine building

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-090`, `cuda-095`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Define the shape envelope.
- Reject an invalid request.
- Separate export build and execution.
- Choose calibration data.
- Record engine compatibility.
- Compare task quality.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-109_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-109_cpu.py
```

```python
def accepted(batch, sequence):
    return 1 <= batch <= 8 and 1 <= sequence <= 32


assert accepted(1, 32)
assert not accepted(9, 16)
assert not accepted(2, 0)
print("CPU deployment contract: supported shapes accepted; invalid shapes rejected")
```

**Expected observation:** Declared shape envelope enforced.

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-109.md) before opening hints.

### Exercise 1: Define the shape envelope

**Trap to avoid:** Leaving the envelope implicit means unsupported shapes reach the engine and fail with internal errors or are padded and truncated without notice.

### Exercise 2: Reject an invalid request

**Trap to avoid:** Splitting batch 9 into 8 and 1 automatically may be reasonable, but only as a documented path. Doing it implicitly changes latency and behavior without a contract.

### Exercise 3: Separate export build and execution

**Trap to avoid:** Reporting the deployment as working because the export succeeded skips build and execution, where unsupported operators and precision problems usually appear.

### Exercise 4: Choose calibration data

**Trap to avoid:** Calibrating on a handful of constant inputs gives ranges that clip real activations, which lowers accuracy. Values outside the calibrated range saturate at the limit, so large activations lose their differences entirely.

### Exercise 5: Record engine compatibility

**Trap to avoid:** Copying an engine file to a different GPU model or runtime release can fail to load or behave differently. Rebuilding per target from the same exported graph is the safer pattern.

### Exercise 6: Compare task quality

**Trap to avoid:** Comparing only a few output tensors for closeness can miss a quality drop concentrated in some classes.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Write the allowed range for every dimension, batch and sequence length included, together with the accepted dtypes.
2. Check a batch of 9 against the envelope before any execution and decide what message the caller should receive.
3. Ask what each step proves on its own: that the model exported, that an engine was built and that the engine produced correct outputs.
4. Ask which data split calibration may read, and why it must not overlap the examples used for evaluation.
5. List what a cached engine depends on, such as the device, toolkit and runtime versions, and record each one with the cache.
6. Run the source model and the engine on the same held-out examples with the same metric, not only a shape check.

## Common mistakes and self-check

A common mistake is treating a successful export or engine build as proof that deployment works. Export can succeed while execution fails, and an engine can execute while a lower precision quietly degrades classification quality beyond tolerance. Another mistake is silently truncating a request outside the declared shapes, such as batch 9 when the envelope stops at 8. Fix both by enforcing the shape envelope with a clear error, keeping the source model and build recipe and comparing task quality on held-out data at every precision you ship.

**Misconception:** An engine built and cached on one machine can be copied to any other deployment host. **Correction:** Engine caches can depend on the GPU model, toolkit and runtime versions used at build time. Treat a cached engine as tied to its build environment: record that environment, rebuild from the preserved source model and recipe for each target, and recheck outputs and quality after every rebuild.

**Evidence limit:** The reference enforces a declared shape envelope in Python and rejects an out-of-range request. It does not export a model or build a TensorRT engine, so operator support, calibration effects, cache compatibility and timing need a prepared runtime on the target hardware, measured separately for build, cold start and warm inference.

1. Why is one successful shape weak evidence for an engine?
2. Why keep calibration data separate from evaluation data?
3. Can an engine cache be copied to another machine safely?

Answers: [self-check answers](../solutions/cuda-109_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-109: Deployment runtimes and engine building.
Read courses/cuda/python/guides/cuda-109.md and courses/cuda/python/lessons/cuda-109.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
