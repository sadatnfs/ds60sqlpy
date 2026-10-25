# cuda-017: explanatory solutions

## Mechanism review

Shared memory lets threads in one block communicate through a common scratch array. Communication requires ordering: a consumer must not read a location until its producer has written it. `__syncthreads()` is a block barrier with memory-ordering effects for participating threads. Put bounds predicates around loads and stores while keeping the required barrier participation uniform. Invalid tail lanes can load a neutral value and still reach the barrier. A barrier does not coordinate ordinary independent blocks, and a memory fence does not force other threads to arrive at the same program point.

The separate [CPU reference](../references/cuda-017_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Four threads load \([3,6,9,12]\) into a shared tile, synchronize, then thread t reads tile[3-t]. The reversed output is \([12,9,6,3]\). Without the barrier, a consumer could read before another thread loads its value. An apparent success on one execution is not a synchronization proof.

## Exercise 2

For a three-element tail in a four-thread block, lane three loads a neutral zero and still participates in the barrier. Only valid lanes store output. A conditional `if (i<n) { load; barrier; }` can violate the barrier contract when some block threads skip it.

## Exercise 3

Thread three produces tile\([3]\), the barrier establishes availability, and thread zero consumes it.

## Exercise 4

Move the required barrier outside the bounds condition, neutralize invalid loads and predicate only accesses that need valid indices.

## Exercise 5

Other blocks do not participate. Use separate dependent kernel stages or a qualified cooperative launch design.

## Exercise 6

Name owners for interior and halo loads, synchronize before consumption, define boundary values and keep output separate from input.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-017_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Name owners for interior and halo loads, synchronize before consumption, define boundary values and keep output separate from input.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
