# cuda-112: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate median speedup

Divide baseline median by candidate median.

**Approach.** Compute the median speedup: baseline samples `[10, 11, 9]` have median 10 and candidate `[8, 8, 9]` has median 8, so the ratio is `10/8 = 1.25`.

**Why it is correct here.** Medians resist a single outlier sample, and the ratio of medians states how much faster the typical candidate run is in this fixture.

**A plausible wrong approach.** Computing the ratio of the fastest samples, `9/8`, picks favorable outliers, while three samples are too few to support a precise estimate either way.

**How to verify.** The reference asserts `speedup == 1.25` and labels the report `gpu_benchmark: False`, since these are synthetic numbers rather than measurements.

## Exercise 2: Preserve raw observations

Keep samples and conditions.

**Approach.** Preserve raw observations: store each sample together with the conditions under which it was measured, such as the device, clocks, versions and input shape.

**Why it is correct here.** Summaries can be recomputed from raw data, and conditions explain variation. Keeping only the median prevents checking spread or outliers later.

**A plausible wrong approach.** Reporting only the speedup ratio discards the information needed to judge whether it is meaningful. With samples such as 9, 10 and 11, the spread is as large as part of the claimed gain, which a single ratio hides.

**How to verify.** Recompute the median from the stored samples and confirm it matches the reported value.

## Exercise 3: Check equivalence first

Fail correctness before performance acceptance.

**Approach.** Check equivalence first: compare candidate output with baseline output within tolerance before evaluating performance.

**Why it is correct here.** A faster kernel that computes something different is not an optimization. The speed ratio then measures two different behaviors.

**A plausible wrong approach.** Accepting a candidate on speed and checking correctness afterward risks deploying a wrong result if the check is skipped. A kernel that skips work, for example by mishandling the tail, will often look faster precisely because it is wrong.

**How to verify.** Make the correctness assertion a gate that stops the review before timing results are reported.

## Exercise 4: Separate cold and warm costs

Report both boundaries.

**Approach.** Separate cold and warm costs: report the first run, with compilation, plan creation and allocation, separately from the steady-state median.

**Why it is correct here.** Short jobs pay cold costs every time, while long-running services amortize them. Both boundaries are needed for different uses.

**A plausible wrong approach.** Mixing the cold run into warm samples raises one sample sharply and can shift the median with only three samples.

**How to verify.** Label each sample cold or warm and compute statistics on warm samples only. Keep the cold sample in the report as its own number, since it is a real cost for short-lived processes.

## Exercise 5: Write supported platform scope

Name exactly tested hardware and software.

**Approach.** Write the supported platform scope naming exactly the tested hardware, driver, toolkit and framework versions.

**Why it is correct here.** Performance results apply to the tested platform. Naming it prevents readers from assuming the result holds on other GPUs.

**A plausible wrong approach.** Stating the speedup for all NVIDIA GPUs generalizes from one device. Memory bandwidth, cache size and clock behavior differ by architecture, so the ratio can change or reverse on other hardware.

**How to verify.** Compare the scope statement with the recorded environment from the run and confirm every item is listed.

## Exercise 6: Prepare a reproducibility checklist

Include source data commands versions metrics and unresolved limits.

**Approach.** Prepare a reproducibility checklist with source revision, input data or generator, exact commands, versions, metrics, and unresolved limitations such as small sample count.

**Why it is correct here.** A checklist allows someone else to rerun the review and see what is still uncertain.

**A plausible wrong approach.** Leaving out the limits, such as only three samples, presents a fragile result as settled. A reader then cannot tell whether a follow-up run that disagrees reveals a regression or ordinary noise.

**How to verify.** Have another person or a clean environment follow the checklist and confirm it reproduces the medians. Any step that required undocumented knowledge to complete should be added to the checklist before the review is closed.

## Reference observation

Synthetic median ratio 1.25; explicitly not a GPU benchmark.

The reference file is `courses/cuda/python/references/cuda-112_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
