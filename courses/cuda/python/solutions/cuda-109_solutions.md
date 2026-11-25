# cuda-109: explained solutions

Compare with your [worksheet](../lessons/cuda-109.md) attempt.

## Exercise 1: Define the shape envelope

List bounded dimensions and dtypes.

**Approach.** Define the shape envelope: batch from 1 to 8, sequence length from 1 to 32 and the accepted dtypes, written as explicit bounds the service checks.

**Why it is correct here.** Deployment engines are often built for bounded dimensions. A declared envelope tells callers what is supported and lets the service reject anything outside it.

**A plausible wrong approach.** Leaving the envelope implicit means unsupported shapes reach the engine and fail with internal errors or are padded and truncated without notice.

**How to verify.** The reference `accepted(batch, sequence)` asserts that `(1, 32)` is accepted and `(9, 16)` and `(2, 0)` are rejected. Add both boundary values to the test.

## Exercise 2: Reject an invalid request

Return a clear error before unsafe execution.

**Approach.** Reject an invalid request such as batch 9 before execution with an error naming the violated bound, rather than truncating input to 8.

**Why it is correct here.** Silent truncation returns results for fewer examples than requested and the caller cannot tell. An explicit error is safe and actionable.

**A plausible wrong approach.** Splitting batch 9 into 8 and 1 automatically may be reasonable, but only as a documented path. Doing it implicitly changes latency and behavior without a contract.

**How to verify.** Send a batch of 9 and assert the error message, then send 8 and confirm success.

## Exercise 3: Separate export build and execution

Each is a separate evidence step.

**Approach.** Separate export, engine build and execution as distinct evidence steps: exporting the model graph, building an engine for a device and running inference each can fail independently.

**Why it is correct here.** A successful export does not mean the engine builds, and a successful build does not mean outputs are correct. Recording each step shows how far validation reached.

**A plausible wrong approach.** Reporting the deployment as working because the export succeeded skips build and execution, where unsupported operators and precision problems usually appear.

**How to verify.** Record pass or fail for each step with its version, and run inference on known inputs before calling the deployment validated.

## Exercise 4: Choose calibration data

Use representative training-side data without evaluation leakage.

**Approach.** Choose calibration data for lower precision from representative training-side samples, never from the held-out evaluation set.

**Why it is correct here.** Calibration sets scale factors from observed value ranges, so unrepresentative data gives poor ranges. Using evaluation data leaks it into the build.

**A plausible wrong approach.** Calibrating on a handful of constant inputs gives ranges that clip real activations, which lowers accuracy. Values outside the calibrated range saturate at the limit, so large activations lose their differences entirely.

**How to verify.** Record which samples were used and assert no overlap with evaluation example IDs.

## Exercise 5: Record engine compatibility

Store runtime device and build metadata.

**Approach.** Record engine compatibility metadata: the runtime version, device model and compute capability, precision mode and shape envelope used during the build.

**Why it is correct here.** Built engines are often tied to a runtime version and GPU architecture. Metadata allows a service to refuse an engine built for a different setup.

**A plausible wrong approach.** Copying an engine file to a different GPU model or runtime release can fail to load or behave differently. Rebuilding per target from the same exported graph is the safer pattern.

**How to verify.** Check stored metadata against the current environment when loading and fail clearly on mismatch.

## Exercise 6: Compare task quality

Evaluate the same held-out examples and metrics.

**Approach.** Compare task quality between the original model and the built engine on the same held-out examples with the same metric, such as classification accuracy.

**Why it is correct here.** Lower precision can change outputs. A successful build only shows the engine runs, so quality must be measured against the application's tolerance.

**A plausible wrong approach.** Comparing only a few output tensors for closeness can miss a quality drop concentrated in some classes.

**How to verify.** Report both accuracies on the same examples and accept only if the drop is within the declared tolerance.

## Self-check answers

1. **Why is one successful shape weak evidence for an engine?** Implementations are chosen per shape, precision and hardware, so other shapes in the contract can fail or behave differently.

2. **Why keep calibration data separate from evaluation data?** Calibrating on evaluation examples tunes the engine to them and makes reported quality optimistic.

3. **Can an engine cache be copied to another machine safely?** Not by assumption. It can depend on the hardware, toolkit and runtime versions, so record them and rebuild or requalify when they differ.

## Reference observation

Declared shape envelope enforced.

Asserted by `courses/cuda/python/references/cuda-109_cpu.py`.
