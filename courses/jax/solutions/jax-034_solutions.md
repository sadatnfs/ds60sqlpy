# jax-034: explained reference

For \(Y=AX+B\) with scalar A=a, \(\partial L/\partial X=aG\), where \(G=\partial L/\partial Y\). At a=3 and G=4, the input gradient is 12, not three or one. For matrix operations, orientation and layout must be translated explicitly. A forward-only comparison cannot establish the derivative or memory-access contract.

## Solution approach

Treat a custom kernel or FFI call as a new component that must earn its place. Start from a measured limitation of a correct high-level baseline, define the accepted layouts and transformations explicitly, validate values and derivatives against an independent oracle, and only then benchmark completed work on named hardware. The closing review defends one concrete claim per evidence layer.

**Why it is correct here:** A lower-level API is not itself a benefit, so the justification must name a bottleneck. A shape does not fix strides, so layout needs a stated policy. A VJP rule does not supply JVP, `vmap` or higher derivatives. Timing that omits synchronization or transfers measures dispatch. Without a GPU, derivation and a CPU reference remain honest progress.

## Exercise 1: Justify the extension

Complexity is justified by a concrete benefit and an acceptance plan, not by the API's lower level.

**Expected:** A measured limitation, equivalent work definition, supported target and independent numerical oracle.

Retain the high-level baseline and state the bottleneck the extension is intended to address.

**Plausible wrong approach:** Writing a kernel because the high-level version feels slow, without a profile, adds maintenance with no demonstrated gain. The baseline and its bottleneck must be measured first.

## Exercise 2: Define input layout

A shape alone does not describe memory layout. Silently assuming contiguity can return wrong values or access invalid memory.

**Expected:** Either correct support or an explicit validated refusal/copy policy.

Include a noncontiguous counterexample and retain the resulting policy in the public interface.

**Plausible wrong approach:** Indexing a transposed input as if it were contiguous reads the wrong elements or invalid memory. A noncontiguous counterexample exposes the assumption before users meet it.

## Exercise 3: Qualify transformation composition

A valid reverse rule does not imply every other transformation mode is implemented.

**Expected:** No; each required transformation needs its own supported rule and evidence.

Test the compositions actually advertised and explicitly reject or exclude unsupported ones.

**Plausible wrong approach:** Assuming `vmap` works because `jax.grad` does confuses two transformation rules. Each advertised transformation needs its own implementation and test, or an explicit refusal.

## Exercise 4: Design a fair kernel benchmark

A faster dispatch-only measurement or omitted transfer is not a valid completed-work speedup.

**Expected:** Matched inputs/outputs, synchronization, warmup, transfers, allocation policy and actual hardware identity.

Validate values and derivatives first, then retain repeated timings and a profile of the measured boundary.

**Plausible wrong approach:** Timing the fused operator without `block_until_ready` while timing the baseline after readback compares dispatch with completed work. The comparison then favors whichever side skipped synchronization.

## Exercise 5: Preserve a CPU oracle

Unavailable hardware limits execution evidence but does not prevent rigorous source and numerical preparation.

**Expected:** Mathematical derivation, small CPU reference, interface review and planned failure cases, with GPU acceptance pending.

Mark compilation, runtime, device correctness and profiling separately; do not fabricate a passed GPU check.

**Plausible wrong approach:** Writing a passed GPU check into the record when no GPU was available fabricates evidence. Compilation, runtime, device correctness and profiling stay marked as pending.

## Exercise 6: Defend the final result

The reviewer should be able to challenge a concrete claim and identify the observation supporting it. A lesson-completion count is not the evidence.

**Expected:** A reproducible artifact and argument covering purpose, assumptions, source, tests, runtime observations, limits and unresolved risks.

Use an unfamiliar input or failure case, explain the diagnosis, and propose a test that would distinguish your repair from a plausible alternative.

**Plausible wrong approach:** Defending the final component with the number of lessons completed answers the wrong question. A reviewer needs a claim, the observation behind it and a test that could refute it.

## How to verify

Check the review against its own evidence: every stated benefit cites a measurement, every supported layout and transformation has a test, and every pending GPU item is labeled pending. Then pose one unfamiliar input, such as a transposed operand, and confirm the plan predicts whether it is handled or refused.

## Scope of this evidence

Do not advertise unsupported dtype/layout/transform combinations. A successful source build is not device correctness, and a correct value is not a valid backward rule. Preserve resource ownership and the high-level oracle throughout optimization.

Select one optional extension only after identifying an actual need. Produce a scoped design and qualification matrix before preparing the external toolchain. The default JAX CPU course remains complete without custom kernels, paid services or accelerator access.
