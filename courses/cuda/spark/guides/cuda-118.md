# cuda-118: Columnar batches, Arrow and data movement

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-113`, `cuda-117`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **count fixed-width payload**, **locate row-column transitions**, and **design a conversion parity test** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Columnar execution groups values by column with accompanying validity and offset structures. Arrow defines interoperable columnar formats; it is not itself a guarantee of GPU residency or zero-copy across every process and device boundary. Variable-width strings need offsets and character storage, while nullable columns need validity information. A batch's byte size can vary greatly with its schema.

Spark's row-to-columnar and columnar-to-row transitions can add work around unsupported operators. Host-to-device and device-to-host transfers are further boundaries. Plan batches by bytes as well as row counts and include temporary decoded representations. Increasing batch size can improve amortization while raising peak memory and spill risk. Preserve schema and null behavior through every conversion.



## Worked examples

### Worked example 1

One thousand float64 values occupy 8000 payload bytes, plus any null mask and metadata. One thousand strings can occupy widely different storage depending on lengths.

### Worked example 2

A validity mask for nine rows needs at least two bytes at one bit per row. Treating null as numeric zero would erase information rather than merely change representation.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows, itemsize = 1000, 8
payload = rows * itemsize
mask = (9 + 7) // 8
assert payload == 8000 and mask == 2
strings = ["a", "longer", ""]
assert sum(len(s.encode("utf-8")) for s in strings) == 7
print("CPU columnar ledger:", payload, mask, 7)
```

**Expected observation:** Fixed payload 8000 bytes, nine-row mask 2 bytes, string characters 7 bytes.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Count fixed-width payload

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **count fixed-width payload** in the examples above.

### Exercise 2: Count validity bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **count validity bytes** in the examples above.

### Exercise 3: Explain string offsets

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **explain string offsets** in the examples above.

### Exercise 4: Locate row-column transitions

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **locate row-column transitions** in the examples above.

### Exercise 5: Budget transfer payload

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **budget transfer payload** in the examples above.

### Exercise 6: Design a conversion parity test

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design a conversion parity test** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Count fixed-width payload".
2. Change one assumption in worked example 2 while preserving the declared contract: count validity bytes.
3. Trace the CPU program's variables before adding hardware behavior: explain string offsets.
4. Draw producers, consumers and the exact operation boundary for the task "Locate row-column transitions".
5. Separate what the small fixture establishes from what the real runtime must show: budget transfer payload.
6. Write a counterexample to an overbroad claim before you design a conversion parity test.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Count fixed-width payload`. For the final claim use `Design a conversion parity test`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-118` using `courses/cuda/spark/guides/cuda-118.md` and `courses/cuda/spark/lessons/cuda-118.md`. Help me reason about Columnar batches, Arrow and data movement. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
