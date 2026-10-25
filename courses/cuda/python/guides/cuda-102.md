# cuda-102: LLM inference, KV caches and precision

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-095`, `cuda-100`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive cache bytes**, **compare cached logits**, and **label fake versus real quantization** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Autoregressive generation separates prefill, which processes an input sequence, from decode, which adds one token repeatedly. A key-value cache stores previous attention projections so decode can reuse them. Cache size grows with layers, batch, sequence length, key/value head count, head dimension and element width. Grouped-query architectures require the actual KV-head count, not necessarily the query-head count.

Weight quantization changes one memory category; it does not automatically quantize the cache or every activation. Educational rounding examples demonstrate error but do not establish packed low-bit execution. Compare cached and uncached logits at each step, bound generation length, and measure prefill and token latency separately. State positional-encoding and mask conventions when testing cache equivalence.

## Derive a cache budget before serving requests

For a dense key/value cache with \(L\) layers, batch \(B\), stored positions \(T\), KV heads \(H_{kv}\), head width \(d_h\), and element width \(s\) bytes:

\[
\text{cache bytes}=2LBTH_{kv}d_hs.
\]

The factor two accounts for keys and values. This is the tensor payload, not allocator padding, fragmentation, page tables, temporary buffers or scheduler state. A paged cache changes allocation management but does not make its underlying values free. Grouped-query attention can use fewer KV heads than query heads, so inspect the model rather than assuming both counts match.

During prefill, many query positions are processed together. During decode, each new query reads the growing history, often producing a very different arithmetic-intensity pattern. Report time to first token and subsequent token latency separately, and state whether tokenization, sampling and output transfer are included. A throughput gain from batching may increase a single user's queueing delay.

Cache correctness requires position and mask consistency. Compare uncached and cached logits at every step for a small deterministic model, with dropout disabled and the same input prefix. Test batch members with different valid lengths and an explicit maximum generation length. If quantization is introduced, compare output quality and numerical error independently. A fake-quantization rounding exercise remains an educational approximation until a real packed low-bit backend executes and its memory/performance are measured.


## Worked examples

### Worked example 1

For 2 layers, batch 1, sequence 16,4 KV heads, head dimension 8 and 2-byte elements, keys and values consume 4096 bytes in the simple dense model.

### Worked example 2

Doubling sequence length doubles this cache payload even if model weights are unchanged. Reducing weight precision alone leaves this term unchanged.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
layers, batch, seq, heads, dim, width = 2, 1, 16, 4, 8, 2
cache = 2 * layers * batch * seq * heads * dim * width
assert cache == 4096
assert 2 * layers * batch * (2 * seq) * heads * dim * width == 8192
print("CPU KV-cache ledger:", cache, "bytes")
```

**Expected observation:** 4096 bytes, doubling to 8192 at twice the sequence length.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Keep cache tensors' batch, sequence, head and dtype contracts explicit. Compare cached token logits with uncached computation under inference mode and the same positional encoding.

### TensorFlow

Represent cache state with explicit tensors or model inputs/outputs and preserve graph signatures across accepted lengths. Compare each cached step with the uncached reference before export.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Derive cache bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **derive cache bytes** in the examples above.

### Exercise 2: Double the sequence

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **double the sequence** in the examples above.

### Exercise 3: Distinguish query and KV heads

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **distinguish query and KV heads** in the examples above.

### Exercise 4: Compare cached logits

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **compare cached logits** in the examples above.

### Exercise 5: Separate prefill and decode timing

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **separate prefill and decode timing** in the examples above.

### Exercise 6: Label fake versus real quantization

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **label fake versus real quantization** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive cache bytes".
2. Change one assumption in worked example 2 while preserving the declared contract: double the sequence.
3. Trace the CPU program's variables before adding hardware behavior: distinguish query and KV heads.
4. Draw producers, consumers and the exact operation boundary for the task "Compare cached logits".
5. Separate what the small fixture establishes from what the real runtime must show: separate prefill and decode timing.
6. Write a counterexample to an overbroad claim before you label fake versus real quantization.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive cache bytes`. For the final claim use `Label fake versus real quantization`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-102` using `courses/cuda/python/guides/cuda-102.md` and `courses/cuda/python/lessons/cuda-102.md`. Help me reason about LLM inference, KV caches and precision. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
