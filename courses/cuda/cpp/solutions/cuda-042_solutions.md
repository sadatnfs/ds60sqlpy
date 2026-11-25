# cuda-042: explanatory solutions

## Mechanism review

Unified virtual addressing concerns address-space organization; managed memory provides an allocation model whose residency and migration are managed under supported platform rules. Neither term promises uniform access cost. First touch can trigger movement, alternating host/device access can cause repeated migration, and prefetch is a placement hint with its own ordering requirements. Coherent systems, discrete GPUs and WSL can have different capabilities. Query support and use the selected platform's documented contract. A single pointer does not erase the need to reason about which processor owns useful work at each phase.

## Exercise 1

A 64 MiB managed array is initialized by the CPU and then processed repeatedly on a GPU. The first GPU pass may include migration costs that later resident passes do not. Report the first pass separately rather than using a warm result to promise cold-start latency.

**Approach:** Time the first GPU pass over the CPU-initialized 64 MiB managed array separately from later passes.

**Why it is correct:** The first pass may fault and migrate pages to the device, which later resident passes avoid.

**A plausible wrong approach:** Reporting only a warm pass as the speed of managed memory hides the first-touch migration a user pays.

**How to verify:** Record first and steady-state times separately on a GPU and label which pass each number describes.

## Exercise 2

Alternating a full CPU pass and full GPU pass for ten rounds can move the working set repeatedly. A simplified model counts twenty ownership transitions, unlike a batched design with one transfer to each side. Actual migration can occur at finer granularity and depends on platform support.

**Approach:** Batch CPU and GPU passes so data changes owner once per side instead of every round.

**Why it is correct:** Ten alternating rounds model twenty transitions of 64 MiB, or 1,280 MiB of potential movement.

**A plausible wrong approach:** Assuming a single pointer means no data moves ignores that pages follow whichever processor touches them.

**How to verify:** The reference asserts modeled_moved_mib == 1280 and marks actual_migration_measured False.

## Exercise 3

The address identifies a virtual allocation; residency describes where backing data currently lives or is accessible under the platform's memory system.

**Approach:** Separate the virtual address in the pointer from where the backing pages currently reside.

**Why it is correct:** The same address stays valid while pages migrate between host and device memory.

**A plausible wrong approach:** Reading the pointer value to decide whether data is on the GPU treats an address as a location.

**How to verify:** Query residency with the platform's attribute APIs rather than inspecting the pointer.

## Exercise 4

Virtual address convenience does not guarantee sufficient device/host memory, supported oversubscription or acceptable fault/migration behavior.

**Approach:** Check device memory, oversubscription support and fault behavior before relying on managed memory.

**Why it is correct:** A unified address space does not add physical memory or guarantee acceptable migration costs.

**A plausible wrong approach:** Allocating more managed memory than the device holds and assuming it just works can thrash or fail.

**How to verify:** Run a working set larger than device memory on the target and watch for errors or slowdown.

## Exercise 5

Use a declared supported fallback or leave the optional experiment unavailable; do not reinterpret failure as a successful placement operation.

**Approach:** Fall back to a declared path or mark the prefetch experiment unavailable.

**Why it is correct:** An unsupported call did not place any data, so no placement claim follows.

**A plausible wrong approach:** Ignoring the returned error and timing as if prefetch happened credits a nonexistent optimization.

**How to verify:** Check the capability and the call's return status, then log which path ran.

## Exercise 6

Group dependent operations on one processor while data is resident, then transfer ownership deliberately; verify latency and memory constraints still fit.

**Approach:** Group dependent steps on one processor while data is resident, then hand ownership over once.

**Why it is correct:** Fewer handoffs mean fewer migrations of the working set.

**A plausible wrong approach:** Adding prefetch calls inside the alternating loop still moves the data every round.

**How to verify:** Count transitions in the new design and check latency and memory limits still fit.

## Self-check answers

1. **Why report the first GPU pass of worked example 1 separately?** It includes migration from host to device that later resident passes do not pay.
2. **What does unified virtual addressing promise?** One address space for host and device pointers, not uniform access cost or residency.
3. **What is prefetch?** A placement hint that moves data ahead of use; it must still be ordered with the work that uses it.

## Numerical reference and its limits

The [CPU reference](../references/cuda-042_cpu.py) reproduces worked example 1 and prints `{'simplified_transition_volume_MiB': 1280, 'actual_migration_measured': False}`.

## Transfer review

Group dependent operations on one processor while data is resident, then transfer ownership deliberately; verify latency and memory constraints still fit.
