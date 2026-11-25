# cuda-002: explanatory solutions

## Mechanism review

An SM, or streaming multiprocessor, schedules groups of GPU threads and owns finite execution and storage resources. A block is a cooperating group in your program; it is not a physical processor. Blocks can wait for resources and need not run in index order. Within a block, threads are organized into warps, normally 32 threads in CUDA. A warp issues instructions with a set of participating lanes. Registers hold per-thread working values, shared memory supports block cooperation, and device DRAM holds larger arrays. Copy engines may transfer data while computation proceeds, but concurrency depends on hardware and dependencies. Compute capability identifies a hardware feature family; toolkit version identifies software.

## Exercise 1

Draw four SM boxes and a grid of ten blocks. Under the deliberately simplified assumption of one resident block per SM, the grid needs at least three waves: four, four and two blocks. This is an occupancy illustration, not a runtime prediction. Real residency depends on registers, shared memory, threads and architectural limits.

**Approach:** Assign ten blocks to four SM boxes one at a time under the stated one-resident-block rule and count rounds until every block has run.

**Why it is correct:** With at most four blocks running at once, ten blocks need ceil(10 / 4) = 3 rounds: four, four, then two.

**A plausible wrong approach:** Reading the drawing as a timing forecast fails because real residency per SM depends on registers, shared memory and thread limits.

**How to verify:** The reference asserts ceil(10 / 4) == 3 and prints simplified_waves 3; redraw with five SMs and expect two waves.

## Exercise 2

A block with 100 threads occupies four warps. The last warp contains four valid program threads and 28 unused lane positions. A kernel with 100 blocks does not require 10,000 physical arithmetic units. Scheduling reuses execution resources over time. Do not build a dependency that assumes block 0 finishes first.

**Approach:** Divide 100 threads by the warp width of 32 with ceiling division, then count valid lanes in the final warp.

**Why it is correct:** Warps are allocated whole, so 96 threads fill three warps and the remaining 4 threads occupy a fourth with 28 idle lanes.

**A plausible wrong approach:** Using floor division gives three warps and silently drops threads 96 to 99, which then never compute their outputs.

**How to verify:** Check ceil(100 / 32) == 4 from the reference output and verify 100 - 3 * 32 = 4 active lanes in the last warp.

## Exercise 3

Ceiling division by 32 yields one, one and two warps. The second warp in the last case has one program thread.

**Approach:** Apply ceil(n / 32) to each block size 31, 32 and 33 and note which lanes are populated in each warp.

**Why it is correct:** Hardware groups threads into 32-lane warps, so 31 and 32 both fit one warp while 33 spills a single thread into a second.

**A plausible wrong approach:** Assuming 33 threads costs barely more than 32 hides that the second warp still occupies a whole scheduling slot for one lane.

**How to verify:** The reference asserts the list [1, 1, 2] for these sizes; confirm with 64 and 65 giving 2 and 3.

## Exercise 4

Record device model and compute capability from device properties separately from compiler/toolkit, driver and framework versions.

**Approach:** Query device properties for model name and major.minor compute capability, and record nvcc, driver and framework versions in separate fields.

**Why it is correct:** Compute capability describes the silicon's feature set while toolkit 12.x describes the compiler; one machine can mix many valid pairs.

**A plausible wrong approach:** Copying the toolkit string into the capability field makes an inventory claim, for example 12.4, that no GPU actually reports.

**How to verify:** Compare the recorded capability against the device query output and confirm the toolkit field matches nvcc --version independently.

## Exercise 5

Yes. The drawing ignores resource pressure, uneven duration and scheduling effects; it establishes a simplified lower bound only.

**Approach:** List the ignored effects in the drawing: register and shared memory pressure, blocks with unequal runtimes and scheduler order.

**Why it is correct:** If a large block uses too many registers, an SM may hold zero additional blocks, and long blocks delay later ones.

**A plausible wrong approach:** Treating three waves as an exact count would wrongly reject a measured run that shows a staggered fourth group.

**How to verify:** Change the model so one SM is unavailable; ceil(10 / 3) = 4 shows the bound is a lower bound only.

## Exercise 6

Data starts in host storage, is transferred to device allocation, and loads feed SM registers or shared memory. Returned output needs an explicit or framework-managed dependency and transfer.

**Approach:** Trace the 2 MiB array from pageable or pinned host memory, through a copy engine, into a device allocation, then into registers or shared memory.

**Why it is correct:** Each hop is a distinct memory space with its own ownership; the SM can only load what the device allocation already holds.

**A plausible wrong approach:** Passing the host pointer straight to a kernel assumes unified addressing makes host data resident; without managed memory that is an illegal access.

**How to verify:** Draw the path with explicit copy calls and confirm the returned buffer is copied back only after the kernel completes.

## Self-check answers

1. **How many warps does a block of 65 threads occupy, and how many lanes sit idle?** Three warps; the last warp holds one valid thread and 31 unused lanes.
2. **Why is a block not the same thing as an SM?** A block is a cooperating group in your program; the SM is the hardware that hosts one or more resident blocks as resources allow.
3. **What does the copy engine add to the hardware picture?** It moves data between host and device memory, so transfers can overlap with kernel execution when streams and pinned memory permit.

## Numerical reference and its limits

The [CPU reference](../references/cuda-002_cpu.py) reproduces worked example 1 and prints `{'simplified_waves': 3, 'warps_for_100_threads': 4}`.

## Transfer review

Data starts in host storage, is transferred to device allocation, and loads feed SM registers or shared memory. Returned output needs an explicit or framework-managed dependency and transfer.
