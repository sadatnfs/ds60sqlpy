# cuda-114: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: List matrix axes

Include Spark Scala Java plugin CUDA architecture driver GPU and OS.

**Approach.** List the compatibility matrix axes: Spark version, Scala binary line, Java version, plugin release, CUDA runtime, host architecture, driver, GPU model and operating system.

**Why it is correct here.** The plugin jar links against Spark and Scala internals and loads native libraries for a host architecture and CUDA. Each axis can independently break loading or execution.

**A plausible wrong approach.** Treating the jar name as proof of compatibility ignores axes the name does not encode, such as the driver or GPU architecture.

**How to verify.** Fill one row of the matrix for the target cluster and confirm each value is recorded from the environment rather than assumed.

## Exercise 2: Identify a Scala mismatch

Match the declared binary line.

**Approach.** Identify a Scala mismatch: a jar built for Scala 2.12 on a Spark distribution built for 2.13 is rejected, as `compatible('2.13', '2.12', 'x86_64', 'x86_64')` returns False.

**Why it is correct here.** Scala binary lines are not compatible with each other, so classes compiled for one may reference methods that do not exist in the other, which shows up as `NoSuchMethodError`.

**A plausible wrong approach.** Matching only the Spark version number while ignoring the Scala suffix in the jar name leads to runtime linkage errors before any query runs.

**How to verify.** The reference asserts the matching case is accepted and the mismatched case rejected. Read the Scala version from the Spark distribution and the jar's artifact suffix.

## Exercise 3: Distinguish toolkit and driver

The driver is a host/runtime capability.

**Approach.** Distinguish toolkit and driver: the CUDA toolkit is a build-time and library dependency, while the driver is installed on the host and determines which CUDA runtime versions can run.

**Why it is correct here.** A plugin built with a newer CUDA runtime may require a minimum driver version. Having the toolkit installed does not satisfy a missing or older driver.

**A plausible wrong approach.** Checking `nvcc --version` and concluding the host is ready tests the compiler, not the driver the executors will use.

**How to verify.** Record the driver version reported by `nvidia-smi` on each executor host and compare it with the plugin release's stated minimum.

## Exercise 4: Record artifact provenance

Use release version checksum and primary source.

**Approach.** Record artifact provenance: the plugin release version, the checksum of the downloaded jar and the primary source URL it came from.

**Why it is correct here.** Provenance lets reviewers confirm the jar is the published artifact and not a modified or mismatched copy.

**A plausible wrong approach.** Copying a jar from a shared folder without a checksum leaves no way to tell which build it is.

**How to verify.** Compute the checksum of the jar on the cluster and compare with the published value.

## Exercise 5: Design a CPU rollback

Keep ordinary Spark environment and query.

**Approach.** Design a CPU rollback: keep an ordinary Spark configuration without the plugin, plus the same query, so the job can run on CPU if the GPU setup fails.

**Why it is correct here.** The rollback provides both an operational fallback and a semantic reference for comparing GPU results.

**A plausible wrong approach.** Removing CPU configuration once the plugin works means a driver or library failure stops the job entirely.

**How to verify.** Periodically run the rollback configuration and confirm it produces the expected result.

## Exercise 6: Define compatibility acceptance

Require import startup bounded query and expected result on the selected host.

**Approach.** Define compatibility acceptance as import, executor startup, a bounded query and the expected result, all on the selected host with the recorded versions.

**Why it is correct here.** Each step tests a deeper level of integration. A row in the matrix is accepted only when all steps pass there.

**A plausible wrong approach.** Accepting a host because the Spark session started with the plugin listed skips native library loading on executors and actual query execution.

**How to verify.** Store the result of each step for each row and accept the row only with all four passing.

## Reference observation

Illustrative Scala/host-architecture predicate rejects mismatch; not a full compatibility probe.

The reference file is `courses/cuda/spark/references/cuda-114_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
