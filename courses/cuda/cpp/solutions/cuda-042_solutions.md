# cuda-042: explanatory solutions

## Mechanism review

Unified virtual addressing concerns address-space organization; managed memory provides an allocation model whose residency and migration are managed under supported platform rules. Neither term promises uniform access cost. First touch can trigger movement, alternating host/device access can cause repeated migration, and prefetch is a placement hint with its own ordering requirements. Coherent systems, discrete GPUs and WSL can have different capabilities. Query support and use the selected platform's documented contract. A single pointer does not erase the need to reason about which processor owns useful work at each phase.

The separate [CPU reference](../references/cuda-042_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A 64 MiB managed array is initialized by the CPU and then processed repeatedly on a GPU. The first GPU pass may include migration costs that later resident passes do not. Report the first pass separately rather than using a warm result to promise cold-start latency.

## Exercise 2

Alternating a full CPU pass and full GPU pass for ten rounds can move the working set repeatedly. A simplified model counts twenty ownership transitions, unlike a batched design with one transfer to each side. Actual migration can occur at finer granularity and depends on platform support.

## Exercise 3

The address identifies a virtual allocation; residency describes where backing data currently lives or is accessible under the platform's memory system.

## Exercise 4

Virtual address convenience does not guarantee sufficient device/host memory, supported oversubscription or acceptable fault/migration behavior.

## Exercise 5

Use a declared supported fallback or leave the optional experiment unavailable; do not reinterpret failure as a successful placement operation.

## Exercise 6

Group dependent operations on one processor while data is resident, then transfer ownership deliberately; verify latency and memory constraints still fit.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-042_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Group dependent operations on one processor while data is resident, then transfer ownership deliberately; verify latency and memory constraints still fit.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
