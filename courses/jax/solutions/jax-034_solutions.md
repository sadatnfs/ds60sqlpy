# jax-034: explained reference

For \(Y=AX+B\) with scalar A=a, \(\partial L/\partial X=aG\), where \(G=\partial L/\partial Y\). At a=3 and G=4, the input gradient is 12, not three or one. For matrix operations, orientation and layout must be translated explicitly. A forward-only comparison cannot establish the derivative or memory-access contract.

## Exercise 1: Justify the extension

Complexity is justified by a concrete benefit and an acceptance plan, not by the API's lower level.

**Expected:** A measured limitation, equivalent work definition, supported target and independent numerical oracle.

Retain the high-level baseline and state the bottleneck the extension is intended to address.

## Exercise 2: Define input layout

A shape alone does not describe memory layout. Silently assuming contiguity can return wrong values or access invalid memory.

**Expected:** Either correct support or an explicit validated refusal/copy policy.

Include a noncontiguous counterexample and retain the resulting policy in the public interface.

## Exercise 3: Qualify transformation composition

A valid reverse rule does not imply every other transformation mode is implemented.

**Expected:** No; each required transformation needs its own supported rule and evidence.

Test the compositions actually advertised and explicitly reject or exclude unsupported ones.

## Exercise 4: Design a fair kernel benchmark

A faster dispatch-only measurement or omitted transfer is not a valid completed-work speedup.

**Expected:** Matched inputs/outputs, synchronization, warmup, transfers, allocation policy and actual hardware identity.

Validate values and derivatives first, then retain repeated timings and a profile of the measured boundary.

## Exercise 5: Preserve a CPU oracle

Unavailable hardware limits execution evidence but does not prevent rigorous source and numerical preparation.

**Expected:** Mathematical derivation, small CPU reference, interface review and planned failure cases, with GPU acceptance pending.

Mark compilation, runtime, device correctness and profiling separately; do not fabricate a passed GPU check.

## Exercise 6: Defend the final result

The reviewer should be able to challenge a concrete claim and identify the observation supporting it. A lesson-completion count is not the evidence.

**Expected:** A reproducible artifact and argument covering purpose, assumptions, source, tests, runtime observations, limits and unresolved risks.

Use an unfamiliar input or failure case, explain the diagnosis, and propose a test that would distinguish your repair from a plausible alternative.

## Scope of this evidence

Do not advertise unsupported dtype/layout/transform combinations. A successful source build is not device correctness, and a correct value is not a valid backward rule. Preserve resource ownership and the high-level oracle throughout optimization.

Select one optional extension only after identifying an actual need. Produce a scoped design and qualification matrix before preparing the external toolchain. The default JAX CPU course remains complete without custom kernels, paid services or accelerator access.
