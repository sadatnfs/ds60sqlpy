# cuda-114: Compatibility is a tested matrix, not a jar name

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-113`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- List matrix axes.
- Identify a Scala mismatch.
- Distinguish toolkit and driver.
- Record artifact provenance.
- Design a CPU rollback.
- Define compatibility acceptance.

## Mechanism and vocabulary

A working GPU Spark installation matches Spark patch line, Scala binary version, Java runtime, plugin release, CUDA native-library variant, host CPU architecture, Linux userspace, NVIDIA driver and GPU architecture. Spark distributions can carry vendor patches, so a nominal Spark version alone may not establish binary compatibility. The published support matrix and release notes must be checked for the exact selected release.

Record artifacts by version and checksum and keep a known CPU baseline. Do not copy a development SNAPSHOT from a documentation example into a beginner setup. The Scala suffix selects a binary ecosystem; the CUDA classifier selects native-library packaging and is not a substitute for a compatible host driver. A local ARM Mac image architecture and an NVIDIA Linux host architecture are separate concerns. This lesson's compatibility worksheet deliberately does not invent a universally supported version combination.



### Key terms

- **Support matrix:** The published combinations of Spark, Scala, Java, CUDA, driver and GPU architecture that a plugin release was tested on.
- **Scala binary version:** The Scala major and minor line, such as 2.12 or 2.13, that a jar was compiled against and must match.
- **CUDA native-library variant:** The plugin jar build that bundles native libraries for a specific CUDA major version.
- **Artifact checksum:** A recorded hash that proves which exact jar was deployed.

## Worked examples

### Worked example 1

A jar built for Scala 2.12 should not be assumed compatible with a Scala 2.13 Spark distribution. A NoSuchMethodError can indicate binary integration trouble before useful GPU work starts.

### Worked example 2

A package can load on one Linux host but fail to initialize native libraries on another architecture. Version ledger completeness and actual smoke execution are both required.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-114_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-114_cpu.py
```

```python
def compatible(spark_scala, jar_scala, host_arch, jar_arch):
    return spark_scala == jar_scala and host_arch == jar_arch


assert compatible("2.13", "2.13", "x86_64", "x86_64")
assert not compatible("2.13", "2.12", "x86_64", "x86_64")
print("CPU compatibility worksheet: mismatched Scala binary line rejected")
```

**Expected observation:** Illustrative Scala/host-architecture predicate rejects mismatch; not a full compatibility probe.

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-114.md) before opening hints.

### Exercise 1: List matrix axes

**Trap to avoid:** Treating the jar name as proof of compatibility ignores axes the name does not encode, such as the driver or GPU architecture.

### Exercise 2: Identify a Scala mismatch

**Trap to avoid:** Matching only the Spark version number while ignoring the Scala suffix in the jar name leads to runtime linkage errors before any query runs.

### Exercise 3: Distinguish toolkit and driver

**Trap to avoid:** Checking `nvcc --version` and concluding the host is ready tests the compiler, not the driver the executors will use.

### Exercise 4: Record artifact provenance

**Trap to avoid:** Copying a jar from a shared folder without a checksum leaves no way to tell which build it is.

### Exercise 5: Design a CPU rollback

**Trap to avoid:** Removing CPU configuration once the plugin works means a driver or library failure stops the job entirely.

### Exercise 6: Define compatibility acceptance

**Trap to avoid:** Accepting a host because the Spark session started with the plugin listed skips native library loading on executors and actual query execution.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Name every component that must line up, from the Spark line and Scala version to the GPU and operating system.
2. Read the Scala suffix on the jar and compare it with the Scala binary version of the Spark distribution.
3. Ask which one ships inside a package and which one must already be installed on the host.
4. Record each artifact's release version, checksum and the primary source you took it from.
5. Keep an ordinary CPU Spark environment and a query whose expected result is known.
6. Write the steps a selected host must pass: import, startup, a bounded query and the expected result.

## Common mistakes and self-check

A common mistake is choosing jars by name, for example a plugin built for Scala 2.12 on a Scala 2.13 distribution, which can fail with a NoSuchMethodError before any GPU work. Another is copying a development SNAPSHOT from a documentation example, or assuming the CUDA classifier replaces a compatible host driver. Fix these by checking the published support matrix for the exact release, recording versions and checksums and running a bounded smoke query on the selected host with a CPU rollback ready.

**Misconception:** If the plugin jar loads and the Spark session starts, the installation is compatible. **Correction:** Session startup on the driver proves little about executors. Native libraries and the device are initialized on each executor, where a driver, CUDA variant or CPU architecture mismatch can still fail. Count the installation as compatible only after a bounded smoke query runs operators on the GPU and the executed plan confirms it.

**Evidence limit:** The reference applies an illustrative predicate that rejects a Scala or host-architecture mismatch. It is not a full compatibility probe; driver, GPU architecture, vendor Spark patches and native library initialization can only be confirmed by a smoke run on the selected host.

1. Why is a nominal Spark version not enough to establish compatibility?
2. What does the CUDA classifier on a plugin jar select?
3. Are a local ARM Mac image and an NVIDIA Linux host the same concern?

Answers: [self-check answers](../solutions/cuda-114_solutions.md#self-check-answers).

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-114: Compatibility is a tested matrix, not a jar name.
Read courses/cuda/spark/guides/cuda-114.md and courses/cuda/spark/lessons/cuda-114.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
