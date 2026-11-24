# cuda-080: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify a CPU result

Call it CPU model or simulator.

**Approach.** Label a passing CPU loop result as a CPU model or simulator result and state what it covered, such as index coverage for one size, without claiming GPU correctness.

**Why it is correct here.** The CPU run checks the algorithm and index formula. It does not exercise the GPU compiler, the memory model or the hardware scheduler, so the label must match the evidence.

**A plausible wrong approach.** Calling the result GPU verified because the same Python source was used assumes the compiled device code behaves like the interpreter.

**How to verify.** Read each recorded claim and check it names the executor. Any claim about GPU behavior must point to a device run with environment details.

## Exercise 2: Construct a race hidden by serialization

Two updates sharing a read value lose one write.

**Approach.** Construct a race that serial execution hides: two lanes read a counter of 0, each adds 1, and each writes 1. The parallel result is 1 while the serial loop gives 2.

**Why it is correct here.** In serial execution each increment completes before the next read, so no update is lost. The reference contrasts `serial_counter == 2` with `lost_update == 1`.

**A plausible wrong approach.** Concluding the kernel needs no atomics because the simulator printed the right count treats a serial schedule as representative of every parallel schedule.

**How to verify.** Confirm both assertions in the reference pass. Then replace the plain increment with an atomic add in the kernel source and record that the race is now ruled out by construction.

## Exercise 3: Name an unsupported feature

Consult the pinned simulator contract.

**Approach.** Name a feature the simulator may not support or may behave differently with, such as particular atomic operations or memory model details, and look up the pinned simulator documentation for that version.

**Why it is correct here.** Simulator coverage changes between versions, so the honest source is the documentation for the version in use. Guessing from memory risks citing a feature added or removed later.

**A plausible wrong approach.** Assuming anything that runs in the simulator runs identically on hardware ignores that the simulator interprets kernels in Python.

**How to verify.** Record the simulator version and quote the relevant documentation line. If a kernel uses an unsupported feature, mark the simulator result as not applicable for that path.

## Exercise 4: Design the validation ladder

Keep stages separate.

**Approach.** Design a validation ladder: CPU oracle, simulator run, device compile, device run with a small input compared to the oracle, then a run under the memory checker.

**Why it is correct here.** Each rung tests something the earlier rungs cannot. Keeping them separate means a failure points to one layer, such as compilation versus numerical disagreement.

**A plausible wrong approach.** Collapsing the ladder into a single pass/fail end-to-end test hides where a failure came from.

**How to verify.** Record a status per rung: passed, failed or not attempted. Without a GPU, the last three rungs should read not attempted.

## Exercise 5: Choose a tiny debugging input

Use a nonmultiple small enough to hand-trace.

**Approach.** Choose a debugging input that is a non-multiple of the block size yet small enough to trace by hand, for example 5 elements with a block size of 4.

**Why it is correct here.** The input creates a partial final block, so tail-guard bugs show up, while five values allow writing every index and output by hand.

**A plausible wrong approach.** Debugging with a million random elements makes a single wrong index hard to find. A size that is a multiple of the block hides tail bugs.

**How to verify.** Write the expected output for all five indices first, then compare element by element and report the first mismatching index.

## Exercise 6: Write an honest evidence label

GPU correctness remains pending until real execution.

**Approach.** Write an evidence label such as: CPU oracle passed; simulator passed for n = 5; GPU correctness pending a real device run.

**Why it is correct here.** The label states exactly which executors produced which results, so a reader knows what remains unproven. That keeps a simulator success from being reported as hardware validation.

**A plausible wrong approach.** Writing only verified or tests pass gives no executor and invites the reader to assume GPU coverage.

**How to verify.** Check that every label names an executor and a status. A label that mentions a GPU must also cite device and driver details.

## Reference observation

Serial count 2 versus a possible lost-update count 1.

The reference file is `courses/cuda/python/references/cuda-080_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
