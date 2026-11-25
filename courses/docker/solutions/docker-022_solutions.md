# docker-022: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-022.md).

## Exercise 1: Compare a CPU limit with dedicated hardware.

**Expected answer:** A quota constrains time; it does not grant exclusive cores.

**Why:** Shared scheduling and host contention remain. State the actual control rather than translating it into an unsupported performance guarantee.

**Approach:** Read cpus: 0.5 as a scheduler quota: the app may use up to half a CPU's worth of time per period, spread across whatever cores run it.

**Why this is correct:** The kernel still shares those cores with other containers and host processes, so the quota caps usage without reserving hardware.

**A plausible wrong approach:** Advertising the fixture as having half a dedicated core promises isolation that the quota never provides.

**How to verify:** Run a busy loop under cpus 0.5 next to another busy container; both slow, and docker stats shows the capped share rather than a reserved core.

## Exercise 2: Predict the effect of insufficient engine VM memory.

**Expected answer:** Container limits cannot compensate for missing host capacity.

**Why:** The VM allocation bounds the resources the engine can manage. Inspect that layer when several individually modest containers compete.

**Approach:** Add up the configured limits, such as 128m for app and 64m for client, and compare the total with the memory given to the engine's VM.

**Why this is correct:** A limit is a ceiling the engine enforces inside its own allocation; it cannot create memory the VM was never given.

**A plausible wrong approach:** Raising mem_limit on each service when several containers crash together ignores that the VM itself is exhausted.

**How to verify:** Check the VM's memory in the engine settings or docker info; once it covers the sum plus overhead, the shared failures stop.

## Exercise 3: Design a controlled CPU comparison.

**Expected evidence:** Same input and image, one changed limit, several bounded measurements.

**Why:** Control enough variables to make the comparison interpretable. Keep architecture and cache state in the evidence record.

**Approach:** Keep the image, input and cache state fixed, change only cpus, and repeat each timed run several times with a timeout.

**Why this is correct:** One changed variable lets a difference in timing be attributed to the limit and not to a cold cache or a new image.

**A plausible wrong approach:** Comparing one run at cpus 0.5 on a laptop with one run at cpus 2 on another machine mixes architecture and host load into the result.

**How to verify:** The record lists the image ID, platform, cache state and every repeated timing, so someone else can rerun the same comparison.

## Exercise 4: Diagnose slowness without assuming memory failure.

**Expected answer:** Compare CPU throttling, I/O, requests and memory observations.

**Why:** Multiple mechanisms produce slow responses. A memory increase is unjustified when the first failing observation is elsewhere.

**Approach:** Collect several observations before changing anything: CPU throttling, disk I/O, request rate and memory near the 128m ceiling.

**Why this is correct:** Slowness can come from CPU quota, blocking file writes to /data or extra traffic. Memory is just one candidate among them.

**A plausible wrong approach:** Doubling mem_limit at the first slow request leaves a CPU-bound or I/O-bound cause untouched.

**How to verify:** The first observation that departs from normal, such as high throttled time, points to the setting worth changing next.

## Exercise 5: Explain why a single docker stats sample is limited.

**Expected answer:** It does not capture the whole workload or historical peaks.

**Why:** Sampling frequency and timing influence what is visible. Use a bounded series and application timings when investigating an intermittent issue.

**Approach:** Treat the --no-stream output as one snapshot taken at the moment the command ran.

**Why this is correct:** A short spike between snapshots, or a peak an hour ago, does not appear in it, so it cannot describe the whole workload.

**A plausible wrong approach:** Concluding that memory is fine from one quiet sample misses the spike that triggered the reported failure.

**How to verify:** Collect a bounded series at a fixed interval during the workload, alongside application timings, and compare peaks with the limits.

## Exercise 6: Define a safe resource stress boundary.

**Expected evidence:** Small fixed workload, timeout and owned disposable target.

**Why:** The goal is to observe a mechanism, not to consume all host resources. Stop when the named failure or performance condition is established.

**Approach:** Choose a small fixed workload against a container you own, wrap it in a timeout, and name the condition that ends the test.

**Why this is correct:** The goal is to see one mechanism, such as throttling under the 0.5 quota, which a short bounded load already shows.

**A plausible wrong approach:** Running an unbounded fork bomb to find the limit risks the whole host; pids_limit 64 helps but is not a reason to try.

**How to verify:** The test stops at its timeout or named condition, and docker compose ps shows only the owned container affected.

## Check your transfer

The PID limit counts tasks in the container's cgroup, and every thread is a task, so 64 threads across all processes exhausts it even though each thread needs little memory or CPU. Confirm by reading `/sys/fs/cgroup/pids.current` and `pids.max` inside the container during load, or the PIDS column of `docker stats`, which should sit at the limit. The fix is a bounded worker pool, or a deliberately raised limit with a stated reason. If the count stayed well below 64 during the failures, the limit is not the cause and memory mapping limits deserve a look.
