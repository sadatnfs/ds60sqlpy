# docker-022: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

CPU and memory are finite resources shared by containers and other host workloads. Resource controls constrain or weight access; they do not automatically reserve a dedicated physical machine. A process can be throttled, run slowly under contention or be killed after memory pressure, depending on its settings and the kernel.

A CPU quota limits how much CPU time a cgroup can consume over a period. A memory limit constrains accounted memory, with behavior influenced by swap and engine configuration. Containers still share the underlying host or VM budget. Allocating a large limit in Compose does not create physical RAM.

Performance experiments need controlled inputs and measurements. A single fast run can benefit from caches, idle neighbors or a different architecture. Record the workload, image, limits, host allocation and several runs. Avoid deliberately exhausting the host as a lesson demonstration.

The fixture uses modest `mem_limit`, `cpus` and `pids_limit` settings. These are runtime constraints on the teaching process, not proof of a production capacity plan. `docker stats --no-stream` gives a point-in-time view. Observe trends with bounded sampling if you need a rate, and distinguish cumulative values from instantaneous ones.

For a safe experiment, compare a short CPU computation at two modest limits in the disposable project. Keep data size fixed and avoid claiming that a single elapsed time isolates every scheduler effect. Memory fault experiments require deliberately small inputs and a controlled target.

## Exercise 1: Compare a CPU limit with dedicated hardware.

Shared scheduling and host contention remain. State the actual control rather than translating it into an unsupported performance guarantee.

**Expected:** A quota constrains time; it does not grant exclusive cores.

## Exercise 2: Predict the effect of insufficient engine VM memory.

The VM allocation bounds the resources the engine can manage. Inspect that layer when several individually modest containers compete.

**Expected:** Container limits cannot compensate for missing host capacity.

## Exercise 3: Design a controlled CPU comparison.

Control enough variables to make the comparison interpretable. Keep architecture and cache state in the evidence record.

**Expected:** Same input and image, one changed limit, several bounded measurements.

## Exercise 4: Diagnose slowness without assuming memory failure.

Multiple mechanisms produce slow responses. A memory increase is unjustified when the first failing observation is elsewhere.

**Expected:** Compare CPU throttling, I/O, requests and memory observations.

## Exercise 5: Explain why a single docker stats sample is limited.

Sampling frequency and timing influence what is visible. Use a bounded series and application timings when investigating an intermittent issue.

**Expected:** It does not capture the whole workload or historical peaks.

## Exercise 6: Define a safe resource stress boundary.

The goal is to observe a mechanism, not to consume all host resources. Stop when the named failure or performance condition is established.

**Expected:** Small fixed workload, timeout and owned disposable target.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
