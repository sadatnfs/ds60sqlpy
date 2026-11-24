# cuda-112: Reproducible GPU performance review

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-071`, `cuda-085`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate median speedup**, **separate cold and warm costs**, and **prepare a reproducibility checklist** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A performance review should let another person reproduce the computation, understand the comparison and identify its limits. Record source revision, hardware, driver, library versions, workload distribution, dtype, precision policy, warmup, synchronization and competing load. Preserve raw bounded timing samples instead of only the best number. Compare complete equivalent work and quantify variation.

Review correctness evidence before speed claims, including edge cases, error tolerance and any changed algorithm. Separate kernel-only time, transfers, preprocessing, compilation and end-to-end latency. Document unavailable platforms honestly. A result from one device is a result from that device; it does not establish a universal architecture ranking. The final artifact should make an independent reviewer able to say which claim is supported and which experiment is still missing.



### Key terms

- **Median speedup:** The ratio of median baseline time to median candidate time over repeated observations.
- **Raw observations:** The complete set of bounded timing samples, preserved instead of only the best number.
- **Equivalence check:** Verification that both versions compute the same result within a stated tolerance before speed is compared.
- **Cold and warm timing:** Separate measurements of first-run cost and steady-state cost.
- **Platform scope:** The hardware and software on which a result was measured, beyond which it is not a claim.

## Worked examples

### Worked example 1

Baseline samples [10,11,9] and candidate [8,8,9] have medians 10 and 8. The median speedup is 1.25, with only three samples and explicitly limited confidence.

### Worked example 2

If candidate output differs beyond tolerance, the speed ratio remains a measurement of different behavior and cannot be accepted as a valid optimization.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
import statistics

baseline, candidate = [10, 11, 9], [8, 8, 9]
speedup = statistics.median(baseline) / statistics.median(candidate)
assert speedup == 1.25
report = {
    "fixture": "synthetic CPU timing analysis",
    "median_ratio": speedup,
    "gpu_benchmark": False,
}
print(report)
```

**Expected observation:** Synthetic median ratio 1.25; explicitly not a GPU benchmark.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `baseline` | `[10, 11, 9]` |
| `candidate` | `[8, 8, 9]` |
| `speedup` | `1.25` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Calculate median speedup

**Trap to avoid:** Computing the ratio of the fastest samples, `9/8`, picks favorable outliers, while three samples are too few to support a precise estimate either way.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Preserve raw observations

**Trap to avoid:** Reporting only the speedup ratio discards the information needed to judge whether it is meaningful. With samples such as 9, 10 and 11, the spread is as large as part of the claimed gain, which a single ratio hides.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Check equivalence first

**Trap to avoid:** Accepting a candidate on speed and checking correctness afterward risks deploying a wrong result if the check is skipped. A kernel that skips work, for example by mishandling the tail, will often look faster precisely because it is wrong.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Separate cold and warm costs

**Trap to avoid:** Mixing the cold run into warm samples raises one sample sharply and can shift the median with only three samples.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Write supported platform scope

**Trap to avoid:** Stating the speedup for all NVIDIA GPUs generalizes from one device. Memory bandwidth, cache size and clock behavior differ by architecture, so the ratio can change or reverse on other hardware.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Prepare a reproducibility checklist

**Trap to avoid:** Leaving out the limits, such as only three samples, presents a fragile result as settled. A reader then cannot tell whether a follow-up run that disagrees reveals a regression or ordinary noise.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate median speedup".
2. Change one assumption in worked example 2 while preserving the declared contract: preserve raw observations.
3. Trace the CPU program's variables before adding hardware behavior: check equivalence first.
4. Draw producers, consumers and the exact operation boundary for the task "Separate cold and warm costs".
5. Separate what the small fixture establishes from what the real runtime must show: write supported platform scope.
6. Write a counterexample to an overbroad claim before you prepare a reproducibility checklist.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate median speedup`. For the final claim use `Prepare a reproducibility checklist`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-112: Reproducible GPU performance review.
Read courses/cuda/python/guides/cuda-112.md and courses/cuda/python/lessons/cuda-112.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
