# cuda-112: Reproducible GPU performance review

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-071`, `cuda-085`, `cuda-092`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate median speedup.
- Preserve raw observations.
- Check equivalence first.
- Separate cold and warm costs.
- Write supported platform scope.
- Prepare a reproducibility checklist.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-112_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-112_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-112.md) before opening hints.

### Exercise 1: Calculate median speedup

**Trap to avoid:** Computing the ratio of the fastest samples, `9/8`, picks favorable outliers, while three samples are too few to support a precise estimate either way.

### Exercise 2: Preserve raw observations

**Trap to avoid:** Reporting only the speedup ratio discards the information needed to judge whether it is meaningful. With samples such as 9, 10 and 11, the spread is as large as part of the claimed gain, which a single ratio hides.

### Exercise 3: Check equivalence first

**Trap to avoid:** Accepting a candidate on speed and checking correctness afterward risks deploying a wrong result if the check is skipped. A kernel that skips work, for example by mishandling the tail, will often look faster precisely because it is wrong.

### Exercise 4: Separate cold and warm costs

**Trap to avoid:** Mixing the cold run into warm samples raises one sample sharply and can shift the median with only three samples.

### Exercise 5: Write supported platform scope

**Trap to avoid:** Stating the speedup for all NVIDIA GPUs generalizes from one device. Memory bandwidth, cache size and clock behavior differ by architecture, so the ratio can change or reverse on other hardware.

### Exercise 6: Prepare a reproducibility checklist

**Trap to avoid:** Leaving out the limits, such as only three samples, presents a fragile result as settled. A reader then cannot tell whether a follow-up run that disagrees reveals a regression or ordinary noise.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Find the median of each sample list, then divide the baseline median by the candidate median.
2. Keep every timing sample with the conditions under which it was taken, not just the best one.
3. Compare outputs against the declared tolerance before looking at any speed number.
4. Report the first run, with setup and compilation, separately from the warm runs.
5. Name the exact hardware and software you tested on and nothing beyond it.
6. List what another person needs to rerun the comparison and get the same answer.

## Common mistakes and self-check

A common mistake is reporting only the best timing and a single speedup number. That hides variation and conditions, and three samples cannot support a confident ratio. Another is quoting a speedup when the candidate's output differs beyond tolerance, which measures different behavior. Fix both by checking correctness first, keeping raw bounded samples with the source revision, hardware, driver, versions and load conditions, and stating the 1.25 median ratio with its limited confidence.

**Misconception:** Results from one GPU let a reviewer predict the speedup on another GPU. **Correction:** Bandwidth, cache sizes, clocks, driver and library versions all differ between devices. A review should state which device produced each number and treat other devices as untested until they are measured.

**Evidence limit:** The reference computes a median ratio of 1.25 from synthetic samples. It is explicitly not a GPU benchmark; a real review needs repeated synchronized measurements on named hardware and software, and its results apply only to that device.

1. Why prefer the median of raw samples over the best time?
2. Which costs should be reported separately?
3. Does one device's result rank architectures in general?

Answers: [self-check answers](../solutions/cuda-112_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-112: Reproducible GPU performance review.
Read courses/cuda/python/guides/cuda-112.md and courses/cuda/python/lessons/cuda-112.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
