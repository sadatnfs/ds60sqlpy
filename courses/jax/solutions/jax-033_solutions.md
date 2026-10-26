# jax-033: explained reference

Suppose process zero owns three observations and process one owns one. Global mean loss remains \((S_0+S_1)/(N_0+N_1)\), not the mean of local means unless the weighting question is deliberately changed. A replicated global result may be visible on several participants without representing several independent observations. Collective mathematics and collective participation must both be correct.

## Exercise 1: Order initialization

Initialization after device-dependent work can leave the intended distributed contract unavailable or inconsistent.

**Expected:** Initialize first, then inspect distributed devices, then construct arrays under the resulting topology.

Retain configuration identity and fail explicitly if the expected participant/device inventory differs.

## Exercise 2: Distinguish local and global views

Those observations do not establish the unseen shards or a successful global gather.

**Expected:** Only its local addressable shard values and placement.

Use an explicit global validation operation when required; do not silently interpret a partial local view as the whole dataset.

## Exercise 3: Preserve sample identities

A correct collective cannot repair incorrect data partitioning or duplicated sample ownership.

**Expected:** The global objective double-counts some observations and changes the effective population.

Validate IDs/counts and the partition policy before interpreting the global loss.

## Exercise 4: Bound a failure experiment

Unbounded hangs are not acceptable teaching fixtures. Process termination and device recovery remain distinct observations.

**Expected:** A bounded timeout/cancellation plan, retained per-process diagnostics and explicit cleanup responsibility.

Run only on explicitly owned resources; retain source/topology identity and inspect cleanup before a new job.

## Exercise 5: Interpret a local simulation

The actual execution surface determines the scope of the evidence.

**Expected:** It demonstrates the mapped mathematical reduction, not network communication or multi-host performance.

Use the CPU model as a numerical oracle for a later real deployment, retaining separate receipts.

## Exercise 6: Specify a scaling study

Changing total batch size or training semantics can make a throughput comparison scientifically misleading even when both programs complete.

**Expected:** A plan fixing effective data/reduction, recording actual devices, synchronizing work, and separating communication, compilation and execution.

Report the work definition, correctness parity, warmup, repeated completed-work timings and hardware/network limits.

## Scope of this evidence

A correct local tensor shape does not establish global ownership, participation or recovery. Treat unknown outcomes as unknown rather than automatically replaying work. No cluster is launched and no host credentials are accessed by this reading unit.

Write a distributed-run specification another engineer could review before execution: process inventory, device mesh, data partition, collective sequence, output checks, time limits and cleanup. Identify which checks need real hosts and which can first be modeled on CPU.
